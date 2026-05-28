from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import pandas as pd

from .artifacts import ModelBundle, load_bundle
from .features import build_features


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_paths() -> dict[str, Path]:
    root = project_root()
    return {
        "bundle": root / "models" / "traffic_bundle.json",
        "outputs": root / "outputs",
    }


@lru_cache(maxsize=1)
def load_service_bundle() -> tuple[ModelBundle, list[lgb.Booster]]:
    paths = default_paths()
    bundle = load_bundle(paths["bundle"])
    boosters = [lgb.Booster(model_file=str(project_root() / model_file)) for model_file in bundle.model_files]
    return bundle, boosters


def predict_frame(df: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame, ModelBundle]:
    bundle, boosters = load_service_bundle()
    features = build_features(df, bundle.encoders, bundle.fill_values)
    features = features[bundle.feature_order].replace([np.inf, -np.inf], np.nan).fillna(features.median(numeric_only=True))
    preds = np.mean([model.predict(features) for model in boosters], axis=0)
    preds = np.clip(preds, 0.0, 1.0)
    return preds, features, bundle


def load_csv_file(upload_file) -> pd.DataFrame:
    return pd.read_csv(upload_file.file)


def build_submission(df: pd.DataFrame, preds: np.ndarray) -> pd.DataFrame:
    result = pd.DataFrame({"Index": df["Index"], "demand": preds})
    return result
