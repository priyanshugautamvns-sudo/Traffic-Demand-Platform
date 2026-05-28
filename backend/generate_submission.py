from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.artifacts import load_bundle
from backend.app.features import build_features
from backend.app.service import project_root


def main() -> None:
    root = project_root()
    bundle = load_bundle(root / "models" / "traffic_bundle.json")
    test_path = root / "data" / "raw" / "test.csv"
    test_df = pd.read_csv(test_path)
    import lightgbm as lgb

    models = [lgb.Booster(model_file=str(root / model_file)) for model_file in bundle.model_files]
    features = build_features(test_df, bundle.encoders, bundle.fill_values)
    features = features[bundle.feature_order].replace([np.inf, -np.inf], np.nan).fillna(features.median(numeric_only=True))
    preds = sum(model.predict(features) for model in models) / len(models)
    submission = pd.DataFrame({"Index": test_df["Index"], "demand": preds.clip(0.0, 1.0)})
    output = root / "outputs" / "submission.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output, index=False)
    print(json.dumps({"output": str(output), "rows": len(submission)}, indent=2))


if __name__ == "__main__":
    main()
