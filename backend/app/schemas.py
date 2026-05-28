from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class UploadResponse(BaseModel):
    valid: bool
    rows: int
    columns: list[str]
    preview: list[dict[str, Any]]
    warnings: list[str]


class PredictionResponse(BaseModel):
    valid: bool
    rows: int
    preview: list[dict[str, Any]]
    stats: dict[str, float]
    download_name: str


class MetricsResponse(BaseModel):
    metrics: dict[str, Any]
    analytics: dict[str, Any]
    feature_importance: list[dict[str, Any]]

