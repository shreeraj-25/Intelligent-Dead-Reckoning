# Methodology

## Build Discipline

Every module is added only after proving it measurably reduces drift versus
the previous configuration. The core evaluation loop is:

1. Simulate a GNSS outage (15s / 30s / 60s) on a sequence with known ground truth.
2. Run the current pipeline configuration through the outage.
3. Record drift %, RMSE, and (once applicable) speed MAE.
4. Compare against the prior configuration in `src/metrics.build_ablation_table`.

## Fixes Applied to the Base Plan

1. **Raw GNSS, not FusedLocationProviderClient** — the Android app reads
   `LocationManager.GPS_PROVIDER` plus `GnssStatus`/`GnssMeasurementsEvent`
   directly, so the EKF fuses true raw fixes and real signal-quality data
   (satellite count, SNR) rather than an already-filtered location product.
2. **Motion-label leakage check** — rule-derived motion labels are validated
   separately on threshold-boundary windows (see `docs/research_gap.md`).
3. **Calibrated confidence head** — trained with a heteroscedastic Gaussian
   NLL loss (`src/speed_model.heteroscedastic_speed_loss`), not left as an
   unspecified "learned uncertainty."
4. **Parallel real-device data collection** — a handful of real drives are
   recorded from Week 1-2 onward via the Android sensor-logging app, in
   parallel with IO-VNBD work, to sanity-check noise characteristics early.
5. **Explicit magnetometer policy** — see `docs/research_gap.md` and
   `config.MAG_USE_CONTINUOUS`.
6. **Explicit timestamp synchronization step** — `src/preprocess.py` is
   written and unit-tested before any EKF work begins.
7. **Pinned dependencies** — see `requirements.txt`.

## Evaluation Targets

See the Performance Targets table in the root `README.md`, aligned to the
ISRO SIH26168 benchmark (<10% drift during GNSS blackout).
