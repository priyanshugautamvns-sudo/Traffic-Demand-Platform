from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
ROAD_MAP = {"Residential": 1.0, "Street": 2.0, "Highway": 3.0}
WEATHER_MAP = {"Sunny": 0.0, "Foggy": 1.0, "Rainy": 2.0, "Snowy": 3.0}
BOOL_MAP = {"Not Allowed": 0.0, "Allowed": 1.0, "No": 0.0, "Yes": 1.0}
CATEGORY_COLS = ["geohash", "RoadType", "Weather", "LargeVehicles", "Landmarks", "geo_prefix2", "geo_prefix3", "geo_prefix4"]


def _safe_series(series: pd.Series) -> pd.Series:
    return series.fillna("__missing__").astype(str)


def _encode_key_series(series: pd.Series, as_integer: bool = False) -> pd.Series:
    if as_integer:
        return pd.to_numeric(series, errors="coerce").fillna(-1).astype(int).astype(str)
    return _safe_series(series)


def decode_geohash(gh: Any) -> tuple[float, float]:
    if gh is None or (isinstance(gh, float) and math.isnan(gh)):
        return (np.nan, np.nan)
    even = True
    lat = [-90.0, 90.0]
    lon = [-180.0, 180.0]
    for ch in str(gh):
        if ch not in BASE32:
            continue
        cd = BASE32.index(ch)
        for mask in [16, 8, 4, 2, 1]:
            if even:
                mid = (lon[0] + lon[1]) / 2.0
                if cd & mask:
                    lon[0] = mid
                else:
                    lon[1] = mid
            else:
                mid = (lat[0] + lat[1]) / 2.0
                if cd & mask:
                    lat[0] = mid
                else:
                    lat[1] = mid
            even = not even
    return ((lat[0] + lat[1]) / 2.0, (lon[0] + lon[1]) / 2.0)


def parse_timestamp(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    parts = _safe_series(series).str.split(":", n=1, expand=True)
    hour = pd.to_numeric(parts[0], errors="coerce").fillna(0).astype(int)
    minute = pd.to_numeric(parts[1], errors="coerce").fillna(0).astype(int)
    return hour, minute


def _target_encoder_frame(df: pd.DataFrame, target_col: str, column: str, smoothing: float) -> pd.DataFrame:
    global_mean = float(df[target_col].mean())
    stats = df.groupby(column, dropna=False)[target_col].agg(["mean", "count"]).reset_index()
    stats[f"{column}_te"] = ((stats["count"] * stats["mean"]) + (smoothing * global_mean)) / (stats["count"] + smoothing)
    stats[f"{column}_freq"] = stats["count"] / float(len(df))
    return stats[[column, f"{column}_te", f"{column}_freq"]]


def fit_encoders(df: pd.DataFrame, target_col: str = "demand", smoothing: float = 30.0) -> dict[str, dict[str, float]]:
    encoder_maps: dict[str, dict[str, float]] = {}
    work = df.copy()
    work["geo_prefix2"] = _safe_series(work["geohash"]).str[:2]
    work["geo_prefix3"] = _safe_series(work["geohash"]).str[:3]
    work["geo_prefix4"] = _safe_series(work["geohash"]).str[:4]

    for column in ["geohash", "RoadType", "Weather", "LargeVehicles", "Landmarks", "NumberofLanes", "geo_prefix2", "geo_prefix3", "geo_prefix4"]:
        frame = _target_encoder_frame(work, target_col, column, smoothing)
        key_series = _encode_key_series(frame[column], as_integer=(column == "NumberofLanes"))
        encoder_maps[f"{column}_te"] = dict(zip(key_series, frame[f"{column}_te"]))
        encoder_maps[f"{column}_freq"] = dict(zip(key_series, frame[f"{column}_freq"]))

    encoder_maps["global_mean"] = {"__all__": float(work[target_col].mean())}
    encoder_maps["temperature_median"] = {"__all__": float(pd.to_numeric(work["Temperature"], errors="coerce").median())}
    encoder_maps["day_median"] = {"__all__": float(pd.to_numeric(work["day"], errors="coerce").median())}
    return encoder_maps


def _map_with_default(series: pd.Series, mapping: dict[str, float], default: float) -> pd.Series:
    return _safe_series(series).map(mapping).fillna(default).astype(float)


def build_features(df: pd.DataFrame, encoders: dict[str, dict[str, float]] | None = None, fill_values: dict[str, float] | None = None) -> pd.DataFrame:
    encoders = encoders or {}
    fill_values = fill_values or {}
    work = df.copy()
    hour, minute = parse_timestamp(work["timestamp"])
    day = pd.to_numeric(work["day"], errors="coerce").fillna(fill_values.get("day", 0)).astype(int)
    geohash = _safe_series(work["geohash"])
    work["geo_prefix2"] = geohash.str[:2]
    work["geo_prefix3"] = geohash.str[:3]
    work["geo_prefix4"] = geohash.str[:4]
    work["time_bucket"] = hour * 4 + (minute // 15)

    features = pd.DataFrame(index=work.index)
    features["day"] = day.astype(float)
    features["hour"] = hour.astype(float)
    features["minute"] = minute.astype(float)
    features["second"] = 0.0
    features["weekday"] = (day % 7).astype(float)
    features["weekend"] = ((day % 7).isin([5, 6])).astype(float)
    features["month"] = (((day - 1) // 30) % 12 + 1).astype(float)
    features["quarter"] = (((features["month"] - 1) // 3) + 1).astype(float)
    features["is_peak_hour"] = hour.isin([7, 8, 9, 17, 18, 19]).astype(float)
    features["is_business_hour"] = hour.between(9, 17).astype(float)
    features["is_night"] = ((hour < 6) | (hour >= 22)).astype(float)
    features["rush_hour_morning"] = hour.isin([7, 8, 9]).astype(float)
    features["rush_hour_evening"] = hour.isin([16, 17, 18, 19]).astype(float)

    hour_float = hour + (minute / 60.0)
    features["sin_hour"] = np.sin(2.0 * np.pi * hour_float / 24.0)
    features["cos_hour"] = np.cos(2.0 * np.pi * hour_float / 24.0)
    features["sin_weekday"] = np.sin(2.0 * np.pi * (day % 7) / 7.0)
    features["cos_weekday"] = np.cos(2.0 * np.pi * (day % 7) / 7.0)

    road_code = _map_with_default(work["RoadType"], ROAD_MAP, 0.0)
    weather_code = _map_with_default(work["Weather"], WEATHER_MAP, 1.5)
    large_code = _map_with_default(work["LargeVehicles"], BOOL_MAP, 0.0)
    land_code = _map_with_default(work["Landmarks"], BOOL_MAP, 0.0)
    lanes = pd.to_numeric(work["NumberofLanes"], errors="coerce").fillna(fill_values.get("NumberofLanes", 0)).astype(float)
    temp_raw = pd.to_numeric(work["Temperature"], errors="coerce")
    temp_fill = fill_values.get("Temperature", float(temp_raw.median() if not np.isnan(temp_raw.median()) else 0.0))
    temp = temp_raw.fillna(temp_fill).astype(float)

    features["road_code"] = road_code
    features["weather_code"] = weather_code
    features["large_code"] = large_code
    features["land_code"] = land_code
    features["num_lanes"] = lanes
    features["temperature"] = temp
    features["temperature_missing"] = temp_raw.isna().astype(float)
    features["weather_missing"] = work["Weather"].isna().astype(float)
    features["road_missing"] = work["RoadType"].isna().astype(float)
    features["temperature_bin"] = pd.cut(temp, bins=[-100, -5, 5, 15, 25, 35, 100], labels=False, include_lowest=True).astype(float)
    features["is_hot"] = (temp >= 30).astype(float)
    features["is_cold"] = (temp <= 10).astype(float)

    features["lane_efficiency"] = lanes / (1.0 + large_code)
    features["heavy_vehicle_interaction"] = lanes * large_code
    features["road_complexity_score"] = road_code * (1.0 + 0.15 * lanes) + 0.5 * large_code + 0.25 * land_code
    features["weather_severity"] = weather_code
    features["weather_x_hour"] = weather_code * hour_float
    features["roadtype_x_lanes"] = road_code * lanes

    lat_lon = geohash.apply(decode_geohash)
    features["geo_lat"] = lat_lon.apply(lambda x: x[0]).astype(float)
    features["geo_lon"] = lat_lon.apply(lambda x: x[1]).astype(float)
    features["geo_lat_abs"] = features["geo_lat"].abs()
    features["geo_lon_abs"] = features["geo_lon"].abs()
    features["time_bucket"] = work["time_bucket"].astype(float)

    default_mean = encoders.get("global_mean", {}).get("__all__", float(temp.mean()))
    for column in ["geohash", "RoadType", "Weather", "LargeVehicles", "Landmarks", "NumberofLanes", "geo_prefix2", "geo_prefix3", "geo_prefix4"]:
        source = work[column] if column in work.columns else pd.Series(["__missing__"] * len(work), index=work.index)
        safe_series = _encode_key_series(source, as_integer=(column == "NumberofLanes"))
        features[f"{column}_te"] = safe_series.map(encoders.get(f"{column}_te", {})).fillna(default_mean).astype(float)
        features[f"{column}_freq"] = safe_series.map(encoders.get(f"{column}_freq", {})).fillna(0.0).astype(float)

    features["geohash_x_peak"] = features["geohash_te"] * features["is_peak_hour"]
    features["day_hour_interaction"] = features["day"] * features["hour"]
    features["lane_time_interaction"] = features["num_lanes"] * features["time_bucket"]
    features["weather_lane_interaction"] = features["weather_severity"] * features["num_lanes"]

    features = features.replace([np.inf, -np.inf], np.nan)
    for column, value in fill_values.items():
        if column in features.columns:
            features[column] = features[column].fillna(value)
    features = features.fillna(features.median(numeric_only=True))
    return features


def build_fill_values(df: pd.DataFrame) -> dict[str, float]:
    num = pd.DataFrame(
        {
            "Temperature": pd.to_numeric(df["Temperature"], errors="coerce"),
            "NumberofLanes": pd.to_numeric(df["NumberofLanes"], errors="coerce"),
            "day": pd.to_numeric(df["day"], errors="coerce"),
        }
    )
    return {col: float(num[col].median()) for col in num.columns}
