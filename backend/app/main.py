from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .schemas import MetricsResponse, PredictionResponse, UploadResponse
from .service import build_submission, load_service_bundle, predict_frame, project_root

app = FastAPI(title="Traffic Demand API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def outputs_dir() -> Path:
    return project_root() / "outputs"


def latest_submission_path() -> Path:
    return outputs_dir() / "latest_submission.csv"


def read_upload(upload: UploadFile) -> pd.DataFrame:
    try:
        return pd.read_csv(upload.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {exc}") from exc


def validate_frame(df: pd.DataFrame, require_target: bool = False) -> list[str]:
    required = ["Index", "geohash", "day", "timestamp", "RoadType", "NumberofLanes", "LargeVehicles", "Landmarks", "Temperature", "Weather"]
    if require_target:
        required.append("demand")
    missing = [col for col in required if col not in df.columns]
    return missing


@app.on_event("startup")
def warm_cache() -> None:
    load_service_bundle()


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "message": "Traffic demand API is live"}


@app.get("/metrics", response_model=MetricsResponse)
def metrics() -> dict[str, Any]:
    bundle, _ = load_service_bundle()
    return {
        "metrics": bundle.metrics,
        "analytics": bundle.analytics,
        "feature_importance": bundle.feature_importance,
    }


@app.get("/feature-importance")
def feature_importance() -> dict[str, Any]:
    bundle, _ = load_service_bundle()
    return {"feature_importance": bundle.feature_importance, "metrics": bundle.metrics}


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> dict[str, Any]:
    df = read_upload(file)
    missing = validate_frame(df, require_target=False)
    if missing:
        raise HTTPException(status_code=400, detail={"missing_columns": missing})
    preview = df.head(8).round(6).to_dict(orient="records")
    warnings = []
    if df.isna().sum().sum() > 0:
        warnings.append("File contains missing values; the model will impute them automatically.")
    return {
        "valid": True,
        "rows": int(len(df)),
        "columns": df.columns.tolist(),
        "preview": preview,
        "warnings": warnings,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)) -> dict[str, Any]:
    df = read_upload(file)
    missing = validate_frame(df, require_target=False)
    if missing:
        raise HTTPException(status_code=400, detail={"missing_columns": missing})
    preds, _, _ = predict_frame(df)
    submission = build_submission(df, preds)
    output_path = latest_submission_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output_path, index=False)
    stats = {
        "min": float(submission["demand"].min()),
        "max": float(submission["demand"].max()),
        "mean": float(submission["demand"].mean()),
        "std": float(submission["demand"].std()),
    }
    return {
        "valid": True,
        "rows": int(len(submission)),
        "preview": submission.head(10).round(6).to_dict(orient="records"),
        "stats": stats,
        "download_name": output_path.name,
    }


@app.get("/download-submission")
def download_submission() -> FileResponse:
    path = latest_submission_path()
    if not path.exists():
        raise HTTPException(status_code=404, detail="No submission has been generated yet. Upload a CSV and run predict first.")
    return FileResponse(path, filename="submission.csv", media_type="text/csv")
