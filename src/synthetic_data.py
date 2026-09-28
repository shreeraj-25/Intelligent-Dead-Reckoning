"""
Synthetic vehicle-trajectory generator for pipeline validation.

This is NOT a substitute for IO-VNBD or real recorded drives -- it exists so
the EKF/ZUPT/NHC pipeline can be validated end-to-end (does it actually
converge toward ground truth?) before real datasets are wired in via
src/data_loader.py. Swap in real sequences using the same column schema
once IO-VNBD is downloaded (see data_loader.ALIASES).
"""

import numpy as np
import pandas as pd


def generate_synthetic_drive(duration_s: float = 120.0, hz: float = 50.0,
                              speed_mps: float = 12.0, turn_at_s: float = 60.0,
                              seed: int = 0):
    """
    Generate a simple straight-then-turn vehicle trajectory with realistic
    IMU noise, plus a matching (noisier, lower-rate) GNSS track.

    Returns: (ground_truth_df, imu_df, gnss_df, ref_lat, ref_lon)
      ground_truth_df: timestamp, east, north  (no noise)
      imu_df:          timestamp, accel_x/y/z, gyro_x/y/z
      gnss_df:         timestamp, gnss_lat, gnss_lon, gnss_speed  (1 Hz, noisy)
      ref_lat/ref_lon: the local-tangent-plane origin used to build gnss_df,
                        needed to convert it back to ENU with preprocess.latlon_to_enu
    """
    rng = np.random.default_rng(seed)
    n = int(duration_s * hz)
    t = np.arange(n) / hz

    # True kinematics: straight line, a brief ~90-degree turn, then straight again.
    turn_duration_s = 6.0
    in_turn = (t >= turn_at_s) & (t < turn_at_s + turn_duration_s)
    yaw_rate_true = np.where(in_turn, np.deg2rad(90) / turn_duration_s, 0.0)
    heading = np.cumsum(yaw_rate_true) / hz
    v_east = speed_mps * np.cos(heading)
    v_north = speed_mps * np.sin(heading)
    east = np.cumsum(v_east) / hz
    north = np.cumsum(v_north) / hz

    # Forward acceleration is ~0 at constant speed except a small ramp-up.
    accel_forward_true = np.gradient(speed_mps * np.ones(n), 1 / hz)
    accel_forward_true[:int(2 * hz)] = speed_mps / 2.0  # brief ramp-up from standstill

    # --- Corrupt with realistic MEMS-grade noise + slowly-varying bias ---
    accel_bias = 0.15
    gyro_bias = 0.01
    accel_noise = rng.normal(0, 0.35, n)
    gyro_noise = rng.normal(0, 0.02, n)
    vibration = 0.4 * np.sin(2 * np.pi * 8 * t) * (rng.random(n) < 0.05)  # sporadic pothole-like spikes

    accel_x = accel_forward_true + accel_bias + accel_noise + vibration
    accel_y = rng.normal(0, 0.2, n)          # lateral vibration
    accel_z = 9.81 + rng.normal(0, 0.1, n)   # gravity + noise
    gyro_z = yaw_rate_true + gyro_bias + gyro_noise
    gyro_x = rng.normal(0, 0.01, n)
    gyro_y = rng.normal(0, 0.01, n)

    imu_df = pd.DataFrame({
        "timestamp": t, "accel_x": accel_x, "accel_y": accel_y, "accel_z": accel_z,
        "gyro_x": gyro_x, "gyro_y": gyro_y, "gyro_z": gyro_z,
    })
    ground_truth_df = pd.DataFrame({"timestamp": t, "east": east, "north": north})

    # GNSS at ~1 Hz, noisy, converted back to a fake lat/lon around an arbitrary origin.
    gnss_idx = np.arange(0, n, int(hz))
    ref_lat, ref_lon = 19.0760, 72.8777  # arbitrary origin (Mumbai) -- not meaningful, just a reference point
    R = 6378137.0
    gnss_noise_m = 3.0
    e_noisy = east[gnss_idx] + rng.normal(0, gnss_noise_m, len(gnss_idx))
    n_noisy = north[gnss_idx] + rng.normal(0, gnss_noise_m, len(gnss_idx))
    lat = ref_lat + np.rad2deg(n_noisy / R)
    lon = ref_lon + np.rad2deg(e_noisy / (R * np.cos(np.deg2rad(ref_lat))))
    speed_noisy = speed_mps + rng.normal(0, 0.3, len(gnss_idx))
    gnss_df = pd.DataFrame({
        "timestamp": t[gnss_idx], "gnss_lat": lat, "gnss_lon": lon, "gnss_speed": speed_noisy,
    })

    return ground_truth_df, imu_df, gnss_df, ref_lat, ref_lon
