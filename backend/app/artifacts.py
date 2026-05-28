from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class ModelBundle:
    feature_order: list[str]
    fill_values: dict[str, float]
    encoders: dict[str, dict[str, float]]
    metrics: dict[str, Any]
    feature_importance: list[dict[str, Any]]
    analytics: dict[str, Any]
    model_files: list[str]

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "ModelBundle":
        return cls(
            feature_order=list(payload["feature_order"]),
            fill_values={k: float(v) for k, v in payload["fill_values"].items()},
            encoders={k: {str(kk): float(vv) for kk, vv in v.items()} for k, v in payload["encoders"].items()},
            metrics=payload["metrics"],
            feature_importance=list(payload["feature_importance"]),
            analytics=payload["analytics"],
            model_files=list(payload["model_files"]),
        )


def save_bundle(bundle: ModelBundle, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle.to_json(), indent=2), encoding="utf-8")


def load_bundle(path: Path) -> ModelBundle:
    return ModelBundle.from_json(json.loads(path.read_text(encoding="utf-8")))

