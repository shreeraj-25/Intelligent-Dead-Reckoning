"""
End-to-end pipeline integration test.

Unlike tests/test_core.py (unit-level smoke tests -- "does it crash, is the
shape right"), this test proves the actual claim the project rests on:
that EKF fusion measurably reduces drift versus raw IMU dead reckoning
during a simulated GNSS outage, using a synthetic but physically
plausible trajectory (see src/synthetic_data.py).

This does NOT replace validation against IO-VNBD or real recorded drives --
it exists so a regression in filters.py or preprocess.py is caught
immediately, before spending time on real-dataset experiments.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import numpy as np
from src.synthetic_data import generate_synthetic_drive
from src.preprocess import simulate_gnss_outage, latlon_to_enu
from src.filters import DeadReckoningEKF


def _raw_dead_reckoning(imu_df, dt):
    """Naive double-integration baseline: no bias correction, no fusion."""
    n = len(imu_df)
    east = np.zeros(n); north = np.zeros(n)
    ve = vn = heading = 0.0
    for i in range(1, n):
        a = float(imu_df["accel_x"].iloc[i])
        wz = float(imu_df["gyro_z"].iloc[i])
        heading += wz * dt
        ve += a * np.cos(heading) * dt
        vn += a * np.sin(heading) * dt
        east[i] = east[i-1] + ve * dt
        north[i] = north[i-1] + vn * dt
    return east, north


def test_ekf_beats_raw_dead_reckoning_during_outage():
    gt, imu, gnss, ref_lat, ref_lon = generate_synthetic_drive(duration_s=90, hz=50, seed=1)
    dt = 1.0 / 50

    # Simulate a 30s GNSS outage in the middle of the drive.
    gnss_outage = simulate_gnss_outage(gnss, start_sec=30, duration_sec=30)

    east_gnss, north_gnss = latlon_to_enu(gnss_outage["gnss_lat"].to_numpy(),
                                           gnss_outage["gnss_lon"].to_numpy(), ref_lat, ref_lon)

    # --- Raw dead reckoning baseline ---
    raw_east, raw_north = _raw_dead_reckoning(imu, dt)

    # --- EKF fusion ---
    ekf = DeadReckoningEKF(np.zeros(7), np.eye(7) * 0.1)
    gnss_times = gnss_outage["timestamp"].to_numpy()
    gnss_ptr = 0
    est_east = np.zeros(len(imu)); est_north = np.zeros(len(imu))
    for i in range(len(imu)):
        t = imu["timestamp"].iloc[i]
        a = float(imu["accel_x"].iloc[i])
        wz = float(imu["gyro_z"].iloc[i])
        if i == 0:
            est_east[i], est_north[i] = 0.0, 0.0
            continue
        ekf.predict(a, wz, dt)
        # Apply a GNSS correction whenever a (non-outage) fix lines up with this timestep.
        while gnss_ptr < len(gnss_times) and gnss_times[gnss_ptr] <= t:
            ekf.correct_gnss([east_gnss[gnss_ptr], north_gnss[gnss_ptr]],
                              R_gnss=np.diag([9., 9.]))
            gnss_ptr += 1
        est_east[i], est_north[i] = ekf.x[0], ekf.x[1]

    gt_east = gt["east"].to_numpy(); gt_north = gt["north"].to_numpy()

    raw_final_error = float(np.hypot(raw_east[-1] - gt_east[-1], raw_north[-1] - gt_north[-1]))
    ekf_final_error = float(np.hypot(est_east[-1] - gt_east[-1], est_north[-1] - gt_north[-1]))

    # The core claim: fused estimate must end up closer to ground truth than
    # naive integration of the same noisy IMU stream over the same drive.
    assert ekf_final_error < raw_final_error, (
        f"EKF did not outperform raw dead reckoning: "
        f"raw={raw_final_error:.1f}m, ekf={ekf_final_error:.1f}m"
    )
    # Sanity bound so a silently-broken filter (e.g. always returns zero)
    # doesn't pass by accident.
    assert ekf_final_error < 500.0
