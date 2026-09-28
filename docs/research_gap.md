# Research Gap — Why Existing Solutions Don't Solve This

## Existing pedestrian dead-reckoning apps (e.g. step-counting PDR apps)

- Built for **walking**, not vehicles — position is updated as `pos += step_length × heading_vector`, using accelerometer peak detection for step counting. There is no periodic gait signal in vehicle motion, so this technique does not transfer.
- Heading typically comes from a gyro + magnetometer complementary filter, with **no formal drift-bounding filter** and no accuracy guarantee.
- GNSS correction is usually a simple scale-factor / heading-bias calibration applied when GPS is available — not a real-time adaptive fusion filter.
- No AI/ML component; no vehicle-specific physical constraints (ZUPT, non-holonomic constraints); no formal accuracy benchmark.
- Often requires **manual user input** (turn indication) during GNSS loss — unworkable for a moving vehicle.

## Why our approach is different

| Dimension | Typical pedestrian DR app | This project |
|---|---|---|
| Target | Walking human | Car / two-wheeler |
| Position model | Step-counting | Strapdown INS + AI-predicted velocity |
| Motion source | Step peak detection | AI speed model from continuous IMU |
| Fusion | Simple scale/bias calibration | Adaptive EKF, uncertainty-driven |
| Vehicle physics | None | ZUPT + in-filter non-holonomic constraints |
| Map role | Display only | Active map-matching correction |
| AI/ML | None | Core requirement (speed, motion-class, confidence) |
| Accuracy target | None stated | < 10% drift (ISRO benchmark) |
| Deployment | Phone app only | Phone app + edge-deployable engine |

## Magnetometer policy note

Indoor/pedestrian PDR literature treats magnetometer heading as a reliable absolute reference. In a vehicle this does not hold: the phone sits close to the chassis, engine, and alternator, producing a large, continuously time-varying magnetic offset correlated with engine RPM and electronics — much worse than the localized, mostly static anomalies pedestrian PDR papers address. This project therefore uses the magnetometer **only** for a one-time, gated coarse heading estimate at standstill, never for continuous heading fusion. Primary heading correction comes from gyro integration, GNSS course-over-ground, and the map-matching heading constraint.
