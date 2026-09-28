"""
Central configuration for the Intelligent Dead Reckoning pipeline.
Edit these values rather than hardcoding constants across modules.
"""

# --- Sensor / sampling ---
IMU_TARGET_RATE_HZ = 50          # common resampled rate for accel/gyro
WINDOW_SECONDS = 2.0              # sliding window length for the AI model
GNSS_MAX_SYNC_DELTA_S = 1.0 / (IMU_TARGET_RATE_HZ * 2)  # max allowed GNSS-IMU time delta

# --- Magnetometer policy (see docs/research_gap.md) ---
MAG_FIELD_MIN_UT = 25.0
MAG_FIELD_MAX_UT = 65.0
MAG_USE_CONTINUOUS = False        # never set True — gated, standstill-only use

# --- ZUPT thresholds ---
ZUPT_GYRO_THRESH = 0.05           # rad/s
ZUPT_ACCEL_VAR_THRESH = 0.1       # m/s^2 variance
ZUPT_SPEED_THRESH = 0.3           # m/s

# --- GNSS outage simulation (for evaluation) ---
OUTAGE_DURATIONS_S = [15, 30, 60]

# --- Paths ---
DATA_RAW_IO_VNBD = "data/raw/io_vnbd"
DATA_RAW_INDIA = "data/raw/india_validation"
DATA_PROCESSED = "data/processed"
MODELS_DIR = "models"
RESULTS_DIR = "results"
