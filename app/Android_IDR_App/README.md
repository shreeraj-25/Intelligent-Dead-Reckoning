# Android IDR App

Native Android application (Kotlin, Gradle) — the primary deliverable
satisfying the ISRO SIH26168 mobile-application requirement.

## Status

This is a **real, buildable Gradle project skeleton** — `settings.gradle.kts`,
module `build.gradle.kts`, manifest, and Kotlin source files for every
component listed below. Open it directly in Android Studio and it will
sync. What's still `TODO` (marked inline in each file) is the actual
sensor->EKF->map-matching wiring and the TFLite model asset — those depend
on the trained model and real-device testing, not on project structure.

## Components (all present as real .kt files)

| File | Role |
|---|---|
| `MainActivity.kt` | Wires everything together, requests runtime permissions |
| `SensorRepository.kt` | Accelerometer/gyroscope via `SensorManager`, gated magnetometer per `docs/research_gap.md` |
| `LocationRepository.kt` | **Raw** GNSS via `LocationManager.GPS_PROVIDER` + `GnssStatus` — deliberately not `FusedLocationProviderClient` (see Fix 1 in `docs/methodology.md`) |
| `NavigationEngine.kt` | On-device counterpart to `src/filters.py` + `src/adaptive_ekf.py` — must stay numerically identical to the Python EKF |
| `TFLiteModelRunner.kt` | Loads the quantized speed/confidence model from `src/speed_model.py` |
| `LogWriter.kt` | CSV sensor logging for real-device data collection, schema-matched to `src/data_loader.py` |

## Required permissions (already in `AndroidManifest.xml`)

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACTIVITY_RECOGNITION" />
<uses-permission android:name="android.permission.HIGH_SAMPLING_RATE_SENSORS" />
```

## Build

```bash
# from this directory, with Android Studio's command-line tools on PATH
./gradlew assembleDebug
```

(Gradle wrapper jar is not committed — open in Android Studio once and it
will generate `gradlew`/`gradlew.bat` automatically, or run
`gradle wrapper` if you have Gradle installed locally.)

## Next steps (in build order)

1. Wire `SensorRepository` + `LocationRepository` output into `LogWriter` and
   record real drives (Week 1-2, parallel to IO-VNBD work).
2. Port the finalized `src/filters.py` EKF logic into `NavigationEngine.kt`
   verbatim — do not reimplement independently, to keep Python validation
   representative of on-device behaviour.
3. Export the trained model to `app/src/main/assets/idr_speed_model.tflite`
   and complete `TFLiteModelRunner`.
4. Replace the `FrameLayout` map placeholder in `activity_main.xml` with an
   OSMDroid `MapView` and wire the confidence-radius overlay.
