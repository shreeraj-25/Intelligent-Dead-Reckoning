package com.idr.app

/**
 * On-device counterpart to src/filters.py (DeadReckoningEKF) and
 * src/adaptive_ekf.py. This is the integration point between:
 *   - SensorRepository (IMU) and LocationRepository (raw GNSS) as inputs
 *   - the exported TFLite speed/confidence model (TFLiteModelRunner)
 *   - map-matching against a locally-cached OSM extract
 *
 * The state representation and update equations here MUST stay numerically
 * identical to src/filters.py so that Python-side validation (against
 * IO-VNBD / synthetic data) is representative of on-device behaviour --
 * port, don't reinvent, when the Python EKF is finalized.
 *
 * TODO: port DeadReckoningEKF.predict()/correct_*() from src/filters.py
 * TODO: port adaptive Q/R tuning from src/adaptive_ekf.py
 * TODO: wire TFLiteModelRunner output into correct_ai_speed()
 * TODO: apply gated magnetometer heading (standstill + field-magnitude check
 *       only, see src/orientation.gated_magnetometer_heading) -- never
 *       continuous heading fusion, per docs/research_gap.md
 */
class NavigationEngine {

    data class NavigationState(
        val eastM: Double,
        val northM: Double,
        val confidenceRadiusM: Double,
        val mode: Mode,
    )

    enum class Mode { GNSS_AIDED, DEAD_RECKONING, RECOVERING }

    private var listener: ((NavigationState) -> Unit)? = null

    fun observe(listener: (NavigationState) -> Unit) {
        this.listener = listener
    }

    fun onImuSample(sample: SensorRepository.ImuSample) {
        // TODO: EKF predict step (see src/filters.DeadReckoningEKF.predict)
    }

    fun onGnssFix(fix: LocationRepository.RawFix) {
        // TODO: gnss_quality-equivalent trust scoring, then EKF correct_gnss
    }
}
