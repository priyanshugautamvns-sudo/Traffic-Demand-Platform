export type MetricsPayload = {
  metrics: {
    cv_r2: number;
    cv_rmse: number;
    fold_r2: number[];
    fold_rmse: number[];
    best_iterations: number[];
    oof_residual_mean: number;
    oof_residual_std: number;
    oof_abs_residual_p95: number;
  };
  analytics: Record<string, Array<Record<string, string | number>>>;
  feature_importance: Array<{ feature: string; importance: number }>;
};

export type UploadResponse = {
  valid: boolean;
  rows: number;
  columns: string[];
  preview: Array<Record<string, string | number | null>>;
  warnings: string[];
};

export type PredictionResponse = {
  valid: boolean;
  rows: number;
  preview: Array<Record<string, number>>;
  stats: { min: number; max: number; mean: number; std: number };
  download_name: string;
};

