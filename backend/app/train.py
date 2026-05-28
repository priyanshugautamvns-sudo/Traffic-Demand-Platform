from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold

from .artifacts import ModelBundle, save_bundle
from .features import build_features, build_fill_values, fit_encoders


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def paths_from_env() -> dict[str, Path]:
    root = project_root()
    return {
        "train": Path(os.getenv("TRAIN_CSV", str(root / "data" / "raw" / "train.csv"))),
        "test": Path(os.getenv("TEST_CSV", str(root / "data" / "raw" / "test.csv"))),
        "model_dir": Path(os.getenv("MODEL_DIR", str(root / "models"))),
        "output_dir": Path(os.getenv("OUTPUT_DIR", str(root / "outputs"))),
    }


def numeric_fill_values(frame: pd.DataFrame) -> dict[str, float]:
    values = {}
    for column in frame.columns:
        if pd.api.types.is_numeric_dtype(frame[column]):
            med = float(frame[column].median())
            values[column] = med
    return values


def build_analytics(train_df: pd.DataFrame, preds_oof: np.ndarray) -> dict[str, Any]:
    tmp = train_df.copy()
    tmp["oof_pred"] = preds_oof
    hour = tmp["timestamp"].astype(str).str.split(":", n=1, expand=True)
    tmp["hour"] = pd.to_numeric(hour[0], errors="coerce").fillna(0).astype(int)
    tmp["minute"] = pd.to_numeric(hour[1], errors="coerce").fillna(0).astype(int)
    tmp["time_label"] = tmp["hour"].astype(str).str.zfill(2) + ":" + tmp["minute"].astype(str).str.zfill(2)
    tmp["temp_bin"] = pd.cut(pd.to_numeric(tmp["Temperature"], errors="coerce").fillna(tmp["Temperature"].median()), bins=[-100, -5, 5, 15, 25, 35, 100], include_lowest=True)

    peak = (
        tmp.groupby("hour", as_index=False)["demand"]
        .mean()
        .rename(columns={"demand": "value"})
        .assign(label=lambda x: x["hour"].astype(str).str.zfill(2) + ":00")
    )[["label", "value"]]
    weather = tmp.groupby("Weather", dropna=False)["demand"].mean().reset_index().rename(columns={"Weather": "label", "demand": "value"})
    road = tmp.groupby("RoadType", dropna=False)["demand"].mean().reset_index().rename(columns={"RoadType": "label", "demand": "value"})
    temp_pattern = tmp.groupby("temp_bin", dropna=False)["demand"].mean().reset_index().rename(columns={"temp_bin": "label", "demand": "value"})
    temp_pattern["label"] = temp_pattern["label"].astype(str)
    demand_distribution = pd.cut(tmp["demand"], bins=10).value_counts(sort=False).reset_index()
    demand_distribution.columns = ["label", "value"]
    demand_distribution["label"] = demand_distribution["label"].astype(str)
    geohash = (
        tmp.groupby("geohash", dropna=False)["demand"]
        .agg(["mean", "count"])
        .sort_values(["mean", "count"], ascending=[False, False])
        .head(12)
        .reset_index()
        .rename(columns={"mean": "value", "count": "count"})
    )
    lane = tmp.groupby("NumberofLanes", dropna=False)["demand"].mean().reset_index().rename(columns={"NumberofLanes": "label", "demand": "value"})

    residuals = tmp["demand"] - tmp["oof_pred"]
    residual_sample = (
        tmp.assign(residual=residuals)
        .sample(n=min(250, len(tmp)), random_state=42)[["oof_pred", "demand", "residual"]]
        .round(6)
        .to_dict(orient="records")
    )

    weather["label"] = weather["label"].fillna("Unknown")
    road["label"] = road["label"].fillna("Unknown")

    return {
        "peak_traffic": peak.round(6).to_dict(orient="records"),
        "weather_vs_demand": weather.round(6).to_dict(orient="records"),
        "road_vs_demand": road.round(6).to_dict(orient="records"),
        "temperature_pattern": temp_pattern.round(6).fillna("Unknown").to_dict(orient="records"),
        "demand_distribution": demand_distribution.round(6).fillna("Unknown").to_dict(orient="records"),
        "geohash_top": geohash.round(6).fillna("Unknown").to_dict(orient="records"),
        "lane_profile": lane.round(6).to_dict(orient="records"),
        "residual_sample": residual_sample,
    }


def train_model(train_df: pd.DataFrame, test_df: pd.DataFrame, output_prefix: Path | None = None) -> dict[str, Any]:
    output_prefix = output_prefix or project_root()
    model_dir = output_prefix / "models"
    output_dir = output_prefix / "outputs"
    model_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    fold_models: list[str] = []
    fold_scores: list[float] = []
    fold_rmses: list[float] = []
    fold_best_iters: list[int] = []
    oof = np.zeros(len(train_df), dtype=float)
    feature_importance = None

    for fold, (tr_idx, va_idx) in enumerate(kf.split(train_df), 1):
        tr = train_df.iloc[tr_idx].copy()
        va = train_df.iloc[va_idx].copy()
        encoders = fit_encoders(tr)
        fill_values = build_fill_values(tr)
        X_tr = build_features(tr, encoders, fill_values)
        X_va = build_features(va, encoders, fill_values)
        X_tr = X_tr.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan).fillna(X_tr.median(numeric_only=True))
        X_va = X_va[X_tr.columns].replace([np.inf, -np.inf], np.nan).fillna(X_tr.median(numeric_only=True))
        y_tr = tr["demand"].astype(float).values
        y_va = va["demand"].astype(float).values

        model = lgb.LGBMRegressor(
            objective="regression",
            n_estimators=5000,
            learning_rate=0.03,
            num_leaves=128,
            min_child_samples=25,
            subsample=0.8,
            subsample_freq=1,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.4,
            random_state=42 + fold,
            n_jobs=-1,
            verbosity=-1,
        )
        model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], eval_metric="rmse", callbacks=[lgb.early_stopping(150, verbose=False)])
        pred = model.predict(X_va)
        oof[va_idx] = pred
        fold_score = r2_score(y_va, pred)
        fold_rmse = float(np.sqrt(mean_squared_error(y_va, pred)))
        fold_scores.append(float(fold_score))
        fold_rmses.append(fold_rmse)
        fold_best_iters.append(int(model.best_iteration_ or model.n_estimators))

        booster_path = model_dir / f"traffic_lgb_fold_{fold}.txt"
        model.booster_.save_model(str(booster_path))
        fold_models.append(booster_path.name)

        gain = model.booster_.feature_importance(importance_type="gain")
        if feature_importance is None:
            feature_importance = gain
            feature_names = X_tr.columns.tolist()
        else:
            feature_importance += gain

    feature_importance = feature_importance / max(len(fold_models), 1)
    importance_rows = (
        pd.DataFrame({"feature": feature_names, "importance": feature_importance})
        .sort_values("importance", ascending=False)
        .head(30)
    )
    top_importance = [
        {"feature": str(row.feature), "importance": float(row.importance)}
        for row in importance_rows.itertuples(index=False)
    ]

    feature_order = feature_names
    encoders = fit_encoders(train_df)
    fill_values = build_fill_values(train_df)
    full_features = build_features(train_df, encoders, fill_values)
    full_features = full_features[feature_order].replace([np.inf, -np.inf], np.nan).fillna(full_features.median(numeric_only=True))
    residuals = train_df["demand"].astype(float).values - oof

    metrics = {
        "cv_r2": float(r2_score(train_df["demand"].astype(float).values, oof)),
        "cv_rmse": float(np.sqrt(mean_squared_error(train_df["demand"].astype(float).values, oof))),
        "fold_r2": [float(x) for x in fold_scores],
        "fold_rmse": [float(x) for x in fold_rmses],
        "best_iterations": [int(x) for x in fold_best_iters],
        "oof_residual_mean": float(residuals.mean()),
        "oof_residual_std": float(residuals.std()),
        "oof_abs_residual_p95": float(np.percentile(np.abs(residuals), 95)),
    }

    analytics = build_analytics(train_df, oof)
    bundle = ModelBundle(
        feature_order=feature_order,
        fill_values=fill_values,
        encoders=encoders,
        metrics=metrics,
        feature_importance=top_importance,
        analytics=analytics,
        model_files=[f"models/{name}" for name in fold_models],
    )
    save_bundle(bundle, model_dir / "traffic_bundle.json")
    (model_dir / "feature_importance.json").write_text(json.dumps(top_importance, indent=2), encoding="utf-8")
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (model_dir / "analytics.json").write_text(json.dumps(analytics, indent=2), encoding="utf-8")

    test_pred = predict_test(test_df, bundle)
    submission = pd.DataFrame({"Index": test_df["Index"], "demand": test_pred})
    submission_path = output_dir / "submission.csv"
    submission.to_csv(submission_path, index=False)
    (output_dir / "latest_submission.csv").write_text(submission.to_csv(index=False), encoding="utf-8")

    return {
        "bundle": bundle,
        "submission_path": str(submission_path),
        "submission_rows": int(len(submission)),
        "submission_preview": submission.head(5).round(6).to_dict(orient="records"),
    }


def predict_test(test_df: pd.DataFrame, bundle: ModelBundle) -> np.ndarray:
    import lightgbm as lgb

    boosters = [lgb.Booster(model_file=str(project_root() / model_file)) for model_file in bundle.model_files]
    features = build_features(test_df, bundle.encoders, bundle.fill_values)
    features = features[bundle.feature_order].replace([np.inf, -np.inf], np.nan).fillna(features.median(numeric_only=True))
    preds = np.mean([model.predict(features) for model in boosters], axis=0)
    return np.clip(preds, 0.0, 1.0)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    paths = paths_from_env()
    train = pd.read_csv(paths["train"])
    test = pd.read_csv(paths["test"])
    return train, test


def main() -> None:
    train_df, test_df = load_data()
    result = train_model(train_df, test_df)
    print(json.dumps({
        "submission_path": result["submission_path"],
        "submission_rows": result["submission_rows"],
        "preview": result["submission_preview"],
    }, indent=2))


if __name__ == "__main__":
    main()
