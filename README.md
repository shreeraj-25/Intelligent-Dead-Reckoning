# 🛰️ Intelligent Dead Reckoning (IDR)

### AI/ML-Assisted GNSS-Denied Navigation for Indian Vehicles

*Seamless smartphone navigation through tunnels, underground parking, and urban canyons — no OBD-II or factory-fitted INS required; smartphone-only operation is supported.*

![PS: SIH26168](https://img.shields.io/badge/PS-SIH26168-blue?style=for-the-badge)
![Theme: Smart Vehicles](https://img.shields.io/badge/Theme-Smart%20Vehicles-orange?style=for-the-badge)
![AI Assisted](https://img.shields.io/badge/AI-Assisted-red?style=for-the-badge)
![Edge Deployable](https://img.shields.io/badge/Edge-Deployable-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Kotlin](https://img.shields.io/badge/Kotlin-Android-purple)
![Status](https://img.shields.io/badge/Status-Research%20Prototype-orange)

---

## Project Overview

**Intelligent Dead Reckoning (IDR)** is designed to transform a standalone smartphone into a GNSS-outage-resilient navigation system. When GNSS becomes unavailable in a tunnel, underground parking structure, or dense urban canyon, IDR switches to AI-assisted inertial tracking — without requiring OBD-II or a factory-fitted INS — and is designed to fuse back with GNSS when the signal returns.

Built for the ISRO problem statement **SIH26168**, targeting Indian vehicles that rely solely on a dashboard-mounted smartphone for navigation.

---

## Demo

The intended live demonstration shows the navigation pipeline across GNSS availability, outage, uncertainty growth, and signal recovery:

```text
GNSS AVAILABLE
       ↓
ABSOLUTE POSITION
       ↓
GNSS LOST
       ↓
INERTIAL / DEAD-RECKONING ESTIMATION
       ↓
POSITION UNCERTAINTY
       ↓
GNSS RESTORED
       ↓
POSITION RE-FUSION
```

A demonstration video can be added under `results/videos/` when the final recording is ready.

---

## Key Features

- **AI Speed & Confidence Estimation** — a CNN-GRU model is designed to predict forward vehicle speed, motion class, and calibrated confidence from noisy smartphone IMU signals.

- **Adaptive GNSS+INS Fusion** — an Extended Kalman Filter whose trust in GNSS vs. IMU adapts in real time based on signal quality and AI-predicted confidence.

- **Physics-Grounded Drift Suppression** — Zero-Velocity Update (ZUPT) and in-filter Non-Holonomic Constraints (NHC), rather than relying only on post-hoc smoothing.

- **Offline Map-Matching** — OpenStreetMap road-graph constraints are used to correct drift using real road geometry, gated by filter uncertainty.

- **Confidence-Aware Navigation UI** — designed to display a live uncertainty radius instead of a falsely precise position marker.

- **Dual Deployment Architecture** — the core engine is designed for Android deployment and portable edge-IMU deployment, supporting smartphone and external IMU data sources.

---

## Proposed System Architecture

```text
┌──────────────────────────────────────────────────────────────────────┐
│                      INTELLIGENT DEAD RECKONING                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   IO-VNBD Dataset        Smartphone IMU          External IMU        │
│   (training/eval)        (accel/gyro/mag)       (Bluetooth/USB)     │
│          │                       │                      │             │
│          └────────────┬──────────┴────────────┬─────────┘             │
│                       ▼                       ▼                       │
│             Preprocessing + Timestamp Sync (elapsedRealtimeNanos)    │
│                       │                                              │
│                       ▼                                              │
│             Phone/Sensor Orientation + Gravity Calibration           │
│                       │                                              │
│                       ▼                                              │
│                 IMU Feature Extraction (sliding windows)             │
│                       │                                              │
│                       ▼                                              │
│       AI Model — 1D-CNN → GRU → (speed, motion-class, confidence)   │
│                       │                                              │
│                       ▼                                              │
│          Adaptive EKF Fusion (GNSS + IMU + AI speed + ZUPT + NHC)   │
│                       │                                              │
│                       ▼                                              │
│              Map-Matching (offline OSM road-constrained correction)  │
│                       │                                              │
│                       ▼                                              │
│              Continuous Position + Confidence Radius Output          │
│                       │                                              │
│              ┌────────┴─────────────┐                                │
│              ▼                      ▼                                │
│       Android Application     Edge Software Engine                   │
│       (live sensors, TFLite)  (recorded / external IMU)             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. Preprocessing & Timestamp Synchronization

Aligns accelerometer, gyroscope, and GNSS streams — each delivered on different native clocks/rates — onto a single common EKF update rate before estimation. Timestamps are tagged at capture with `elapsedRealtimeNanos()`; GNSS fixes exceeding half the EKF update period from their nearest IMU sample are flagged and dropped rather than silently misaligned.

### 2. Orientation & Calibration Engine

Estimates the phone-to-vehicle rotation from the gravity vector while stationary, then refines yaw alignment against GNSS course-over-ground once the vehicle is moving straight. Continuously checks for mount disturbance rather than assuming a one-time calibration holds for the whole trip.

### 3. AI Speed & Confidence Model

```text
Input:  2-second IMU window (accel XYZ, gyro XYZ, accel/gyro magnitude, jerk) @ 50Hz

Output: forward speed (μ), motion class, calibrated uncertainty (σ²)

Architecture: 1D-CNN → 1D-CNN → GRU → three heads

Loss: heteroscedastic Gaussian NLL (speed) + smoothness + jerk penalty + classification loss
```

The confidence head is intended to provide a functional uncertainty estimate that can directly control the EKF's measurement-noise term for the AI speed pseudo-measurement.

### 4. Adaptive EKF Fusion Engine

Fuses GNSS position/speed, AI-predicted speed, Zero-Velocity Updates during stops, and Non-Holonomic Constraints (lateral/vertical velocity ≈ 0) enforced inside the filter's correction step. Process and measurement noise adapt in real time to vibration level, GNSS signal quality, and outage duration.

### 5. Map-Matching

Uses a locally available OpenStreetMap road graph for offline map matching and scores nearby road candidates on distance, heading agreement, route continuity, and current filter uncertainty — applying only a soft, uncertainty-weighted correction rather than a hard snap-to-road.

### 6. Edge Deployment

Trained models are intended to be exported to TensorFlow Lite with INT8 post-training quantization and benchmarked for size, latency, and accuracy loss on-device before being used in the final pipeline.

---

## Technology Stack

**Modelling & Research**

```text
Python 3.10/3.11 • PyTorch • NumPy • Pandas • SciPy • Scikit-learn
```

**Sensor Fusion**

```text
FilterPy / custom Extended Kalman Filter (NumPy)
```

**Geospatial / Map-Matching**

```text
OSMnx • Shapely • PyProj • GeoPandas • OpenStreetMap
```

**Edge Deployment**

```text
TensorFlow Lite / LiteRT • INT8 Post-Training Quantization
```

**Mobile Application**

```text
Android Studio • Kotlin • SensorManager • GnssStatus / GnssMeasurementsEvent • OSMDroid
```

**Dataset**

```text
IO-VNBD — Inertial and Odometry Benchmark Dataset for Ground Vehicle Positioning

https://github.com/onyekpeu/IO-VNBD
```

---

## Getting Started

### Prerequisites

```text
Python 3.10 or 3.11
Android Studio (Arctic Fox or later)
Git
```

### 1️⃣ Clone Repository

```bash
git clone https://github.com/<your-org>/intelligent-dead-reckoning.git
cd intelligent-dead-reckoning
```

> Replace `<your-org>` with your actual GitHub username or organization after creating the repository.

### 2️⃣ Python Environment

```bash
python -m venv idr_env
source idr_env/bin/activate     # Windows: idr_env\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Dataset

```bash
git clone https://github.com/onyekpeu/IO-VNBD.git data/raw/io_vnbd
```

### 4️⃣ Run the Exploration Notebook

```bash
jupyter notebook notebooks/01_explore_io_vnbd.ipynb
```

### 5️⃣ Android App

```text
Open app/Android_IDR_App in Android Studio → Gradle sync → Build APK
```

---

## Performance Targets

**These are target benchmarks, not current measured results.**

Aligned with the ISRO SIH26168 benchmark:

| Metric | Target |
|---|---|
| Positional drift during GNSS blackout | < 10% of distance travelled |
| Example | < 5 m drift over 50 m GNSS-denied stretch in < 1 min |
| Example | < 100 m drift over 1 km GNSS-denied stretch at 60 km/h |
| GNSS+INS fusion update rate (mobile) | 10 Hz |
| Fusion update rate (edge engine, Fiber Optic Gyroscope (FOG) IMU) | ~200 Hz |

---

## Current Status

- **`src/`** — all 14 core modules are functionally implemented (EKF with innovation gating, adaptive Q/R tuning, ZUPT, non-holonomic constraints, heteroscedastic speed/confidence model, map-matching, metrics), backed by a unit test suite (`tests/test_core.py`) and an end-to-end integration test (`tests/test_integration_pipeline.py`) that demonstrates measurable improvement from EKF fusion over raw dead reckoning on the current synthetic test pipeline.

- **Validation so far is on synthetic data** (`src/synthetic_data.py`), not yet IO-VNBD or real recorded drives — see [`results/plots/synthetic_baseline_comparison.png`](results/plots/synthetic_baseline_comparison.png) and [`results/tables/synthetic_ablation.csv`](results/tables/synthetic_ablation.csv) for the current baseline numbers. The basic EKF baseline reduces drift roughly 2.5× versus raw dead reckoning on this synthetic drive, but does not yet reach the <10% target — that requires the AI speed model, ZUPT, and map-matching from later phases, as described in the ablation methodology in `docs/methodology.md`.

- **`app/Android_IDR_App/`** — a real, buildable Gradle/Kotlin project skeleton (manifest, permissions, `MainActivity`, `SensorRepository`, `LocationRepository`, `NavigationEngine`, `TFLiteModelRunner`, `LogWriter`) with the sensor/GNSS/EKF wiring marked as explicit `TODO`s pending the trained model and real-device testing.

- **Not yet done:** training against real IO-VNBD sequences, a trained/exported TFLite checkpoint, and real-device validation drives — these are the actual remaining build-phase work, not scaffolding gaps.

---

## Validation & Verification

### Current Validation

| Validation Area | Status | Evidence |
|---|---|---|
| EKF fusion | Implemented | `tests/test_core.py` |
| End-to-end pipeline | Implemented | `tests/test_integration_pipeline.py` |
| Synthetic GNSS outage simulation | Implemented | `src/synthetic_data.py` |
| Raw DR vs EKF comparison | Available | `results/plots/synthetic_baseline_comparison.png` |
| Synthetic ablation analysis | Available | `results/tables/synthetic_ablation.csv` |
| Real IO-VNBD training | Pending | — |
| TFLite model export | Pending | — |
| Real-device validation | Pending | — |

### Current Synthetic Result

The current synthetic baseline shows approximately **2.5× lower drift with EKF fusion compared with raw dead reckoning**.

This result is from synthetic validation and should not be interpreted as real-world vehicle performance.

---

## Testing

The project includes unit tests and an end-to-end integration test.

### Run Core Tests

```bash
pytest tests/test_core.py -v
```

### Run Integration Test

```bash
pytest tests/test_integration_pipeline.py -v
```

### Run All Tests

```bash
pytest tests/ -v
```

The test suite is intended to cover the core estimation pipeline, including EKF behaviour and the end-to-end synthetic pipeline. Test coverage should be expanded as additional modules move from prototype to validated implementation.

> Do not interpret the presence of a test file as proof of real-world vehicle validation. Real-data and real-device validation remain pending.

---

## Reproducing Current Results

The currently published baseline results are based on the synthetic validation pipeline.

```bash
python src/synthetic_data.py
pytest tests/test_integration_pipeline.py -v
```

Generated outputs are stored under:

```text
results/
├── plots/
└── tables/
```

The current results represent synthetic-data validation only. Real IO-VNBD and real-device validation are planned future stages.

---

## Limitations

The current implementation has the following limitations:

- Validation is currently based on synthetic vehicle-motion data.
- Training on real IO-VNBD sequences is not yet completed.
- A trained/exported TFLite checkpoint is not yet included.
- Real-device Android validation is still pending.
- Performance during prolonged GNSS outages has not yet been experimentally established on real vehicles.
- Map-matching performance depends on the availability and quality of the local OpenStreetMap road graph.

These limitations define the remaining validation work rather than representing completed performance claims.

---

## Why This Approach Is Different

- **Calibrated confidence, not decoration** — the AI uncertainty output is designed to provide a meaningful confidence estimate that can control the EKF's trust in the AI speed measurement.

- **NHC applied inside the filter** — rather than relying only on cosmetic post-hoc road snapping.

- **Deliberate magnetometer policy** — used only for gated, one-time coarse heading at standstill, never fused continuously, due to chassis-proximity magnetic distortion in vehicles.

- **One engine, two deployment targets** — smartphone application and external-IMU edge engine share the same core architecture, supporting the intended deployment scope of the problem statement.

---

## Repository Structure

```text
intelligent-dead-reckoning/
│
├── src/                         # Core IDR algorithms
├── app/                         # Android application
│   └── Android_IDR_App/         # Kotlin/Gradle Android project
├── tests/                       # Unit and integration tests
├── notebooks/                   # Dataset exploration & experiments
├── data/                        # Dataset configuration / local data
├── models/                      # Model/checkpoint locations
├── results/                     # Experimental results
│   ├── plots/
│   └── tables/
├── docs/                        # Technical documentation
├── requirements.txt             # Python dependencies
├── RUN.md                       # Project run instructions
├── README.md                    # Project documentation
├── LICENSE                      # Project license
└── .gitignore                   # Ignored local/build files
```

See [`docs/architecture.png`](docs/architecture.png) and [`docs/methodology.md`](docs/methodology.md) for full technical detail.

---

## Research Gap

See [`docs/research_gap.md`](docs/research_gap.md) for a comparison against existing dead-reckoning approaches and why they don't solve this problem.

---

## Research & References

- **IO-VNBD** — Inertial and Odometry Benchmark Dataset for Ground Vehicle Positioning
- **OpenStreetMap** — open geospatial road data
- **Extended Kalman Filter (EKF)** — probabilistic sensor-fusion framework
- **Zero-Velocity Update (ZUPT)** — inertial navigation drift correction
- **Non-Holonomic Constraints (NHC)** — vehicle-motion constraints for inertial navigation

See `docs/methodology.md` and `docs/research_gap.md` for the project's detailed technical discussion and references.

---

## 🙏 Acknowledgments

- IO-VNBD dataset authors (Onyekpe et al.) for the benchmark dataset
- OpenStreetMap contributors for geospatial road data
- ISRO / Department of Space for problem statement SIH26168

---

**Team:** TEAM ZENITH · **Team ID:** 156397 · **SIH 2026**
