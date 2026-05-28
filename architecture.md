# Architecture Diagram

```mermaid
flowchart LR
  U[User] --> F[Next.js 14 Dashboard]
  F -->|upload CSV| A[FastAPI API]
  A --> P[Feature Pipeline]
  P --> M[LightGBM Fold Ensemble]
  M --> S[submission.csv]
  A --> Q[Metrics + Analytics Bundle]
  Q --> F
```

