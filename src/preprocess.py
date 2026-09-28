"""Timestamp synchronization, resampling, GNSS outage simulation and ENU conversion."""
import numpy as np
import pandas as pd
from . import config

_REQUIRED_IMU = ["timestamp", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]

def _time_seconds(s):
    if np.issubdtype(s.dtype, np.number):
        a = s.to_numpy(float)
        # Treat very large values as epoch nanoseconds/milliseconds.
        scale = 1.0
        med = np.nanmedian(np.abs(a)) if len(a) else 0
        if med > 1e17: scale = 1e9
        elif med > 1e14: scale = 1e6
        elif med > 1e11: scale = 1e3
        return pd.Series(a / scale, index=s.index)
    t = pd.to_datetime(s, errors="coerce", utc=True)
    return pd.Series(t.astype("int64") / 1e9, index=s.index)

def resample_imu(df: pd.DataFrame, target_hz: int = config.IMU_TARGET_RATE_HZ) -> pd.DataFrame:
    """Resample IMU channels onto a fixed-rate time grid using interpolation."""
    if target_hz <= 0: raise ValueError("target_hz must be positive")
    missing = [c for c in _REQUIRED_IMU if c not in df.columns]
    if missing: raise ValueError(f"Missing IMU columns: {missing}")
    out = df.copy()
    out["_t"] = _time_seconds(out["timestamp"])
    out = out.dropna(subset=["_t"]).sort_values("_t").drop_duplicates("_t")
    if len(out) < 2: raise ValueError("At least two valid IMU samples are required")
    step = 1.0 / target_hz
    grid = np.arange(out["_t"].iloc[0], out["_t"].iloc[-1] + step * 0.5, step)
    result = pd.DataFrame({"timestamp": grid})
    numeric = [c for c in out.columns if c not in ("timestamp", "_t") and pd.api.types.is_numeric_dtype(out[c])]
    for c in numeric:
        result[c] = np.interp(grid, out["_t"].to_numpy(), out[c].astype(float).to_numpy())
    return result

def align_gnss_to_imu(gnss_df, imu_df, max_delta_s=config.GNSS_MAX_SYNC_DELTA_S):
    """Attach each GNSS fix to the nearest IMU sample; reject fixes outside tolerance."""
    if max_delta_s < 0: raise ValueError("max_delta_s must be non-negative")
    g = gnss_df.copy(); i = imu_df.copy()
    g["_t"] = _time_seconds(g["timestamp"]); i["_t"] = _time_seconds(i["timestamp"])
    g = g.dropna(subset=["_t"]).sort_values("_t"); i = i.dropna(subset=["_t"]).sort_values("_t")
    if i.empty: return pd.DataFrame(columns=list(g.columns) + ["imu_timestamp", "sync_delta_s"])
    idx = np.searchsorted(i["_t"].to_numpy(), g["_t"].to_numpy())
    idx = np.clip(idx, 0, len(i)-1)
    left = np.maximum(idx-1, 0)
    right = idx
    lt = i["_t"].to_numpy()[left]; rt = i["_t"].to_numpy()[right]
    use_right = np.abs(rt-g["_t"].to_numpy()) < np.abs(lt-g["_t"].to_numpy())
    nearest = np.where(use_right, rt, lt)
    keep = np.abs(nearest-g["_t"].to_numpy()) <= max_delta_s
    result = g.loc[keep].copy()
    result["imu_timestamp"] = nearest[keep]
    result["sync_delta_s"] = np.abs(nearest[keep]-result["_t"])
    return result.drop(columns=["_t"])

def simulate_gnss_outage(gnss_df, start_sec, duration_sec):
    if duration_sec < 0: raise ValueError("duration_sec must be non-negative")
    out = gnss_df.copy(); t = _time_seconds(out["timestamp"])
    start = float(start_sec); end = start + float(duration_sec)
    # start_sec is interpreted relative to the first GNSS timestamp when possible.
    rel = t - t.iloc[0] if len(t) else t
    return out.loc[~((rel >= start) & (rel < end))].reset_index(drop=True)

def latlon_to_enu(lat, lon, ref_lat, ref_lon):
    """Small-area WGS84 equirectangular approximation, accurate enough for local trajectories."""
    lat = np.asarray(lat, dtype=float); lon = np.asarray(lon, dtype=float)
    R = 6378137.0
    dlat = np.deg2rad(lat-ref_lat); dlon = np.deg2rad(lon-ref_lon)
    east = R * dlon * np.cos(np.deg2rad(ref_lat))
    north = R * dlat
    return east, north
