# Flipkart Traffic Demand Intelligence

A lightweight hackathon-ready traffic demand prediction platform built with a small FastAPI backend, a polished Next.js 14 dashboard, and a LightGBM model tuned for strong R² with low inference overhead.

## Problem

Predict `demand` from road, weather, geospatial, and time features.

## Stack

- Frontend: Next.js 14, TypeScript, Tailwind CSS, Framer Motion, Recharts
- Backend: FastAPI
- ML: LightGBM with leakage-safe target encoding and KFold validation

## Project Layout

- `frontend/` UI and dashboards
- `backend/` FastAPI app and training pipeline
- `models/` saved model bundle and metrics
- `notebooks/` training notebook
- `outputs/` generated submission and reports
- `data/` local dataset drop zone

## ML Pipeline

1. Parse timestamps into hour-level and minute-level signals.
2. Encode cyclic time features with sine/cosine.
3. Decode geohash to approximate latitude and longitude.
4. Build road, weather, lane, and geospatial interaction features.
5. Fit leakage-safe target encodings with KFold for high-cardinality fields.
6. Train LightGBM folds with early stopping.
7. Average fold predictions for submission generation.

## Features

- Timestamp: `hour`, `minute`, `weekday`, `weekend`, `month`, `quarter`, rush-hour flags, night flag
- Cyclical: `sin_hour`, `cos_hour`, `sin_weekday`, `cos_weekday`
- Geohash: frequency and target encodings, approximate lat/lon, prefix encodings
- Weather: severity mapping, temperature bins, hot/cold indicators
- Road: lane efficiency, heavy vehicle interaction, road complexity
- Interactions: weather × hour, road type × lanes, geohash × peak-hour

## Training

```bash
python backend/train.py
```

This trains the model, saves the bundle into `models/`, and writes `outputs/submission.csv`.

## Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

## Frontend

```bash
npm install
npm run dev
```

## Deployment

See [`DEPLOYMENT.md`](./DEPLOYMENT.md).

## Metrics

The model bundle stores:

- cross-validation R²: `0.9564`
- cross-validation RMSE: `0.02969`
- fold RMSE / R² arrays
- feature importance
- residual summaries
- analytics aggregates for the dashboard

## Screenshots

- [Landing](./outputs/screenshots/landing.png)
- [Prediction](./outputs/screenshots/predict.png)
- [Analytics](./outputs/screenshots/analytics.png)
- [Insights](./outputs/screenshots/insights.png)

## Future Scope

- Optional XGBoost ensemble if it materially improves validation
- SHAP export for deeper explanations
- Hosted demo deployment with a static artifact pipeline
