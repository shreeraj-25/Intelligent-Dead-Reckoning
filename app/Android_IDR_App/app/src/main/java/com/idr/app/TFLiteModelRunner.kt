package com.idr.app

/**
 * Loads the quantized speed/confidence model exported from
 * src/speed_model.py (see docs/methodology.md Phase 5 -- TFLite INT8
 * export) and runs inference on a rolling 2-second IMU window.
 *
 * TODO: load idr_speed_model.tflite from assets/
 * TODO: maintain a rolling window buffer matching src/motion_classifier
 *       .extract_window_features's exact feature order (accel xyz, gyro xyz,
 *       accel magnitude, gyro magnitude, jerk magnitude)
 * TODO: run interpreter.run(), return (speedMps, motionClass, confidence)
 */
class TFLiteModelRunner {
    data class Prediction(val speedMps: Float, val motionClass: Int, val confidenceVariance: Float)

    fun predict(window: FloatArray): Prediction {
        throw NotImplementedError("Load TFLite model and run inference here.")
    }
}
