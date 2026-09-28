package com.idr.app

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.SystemClock

/**
 * Reads accelerometer, gyroscope, and (gated, standstill-only -- see
 * docs/research_gap.md) magnetometer via the native SensorManager API,
 * NOT a fused/abstracted sensor source. Every sample is timestamped with
 * SystemClock.elapsedRealtimeNanos() at capture time so it can be aligned
 * against GNSS fixes downstream (mirrors src/preprocess.py on the Python side).
 */
class SensorRepository(context: Context) : SensorEventListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val accelerometer: Sensor? = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
    private val gyroscope: Sensor? = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
    private val magnetometer: Sensor? = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)

    data class ImuSample(
        val elapsedRealtimeNanos: Long,
        val accelX: Float, val accelY: Float, val accelZ: Float,
        val gyroX: Float, val gyroY: Float, val gyroZ: Float,
    )

    private var onSample: ((ImuSample) -> Unit)? = null
    private var latestAccel: FloatArray? = null
    private var latestGyro: FloatArray? = null

    fun start(targetRateHz: Int = 50, onSample: (ImuSample) -> Unit) {
        this.onSample = onSample
        val samplingPeriodUs = 1_000_000 / targetRateHz
        accelerometer?.let { sensorManager.registerListener(this, it, samplingPeriodUs) }
        gyroscope?.let { sensorManager.registerListener(this, it, samplingPeriodUs) }
        // Magnetometer is registered but MUST only be read via the gated,
        // standstill-only path in NavigationEngine -- never fused continuously.
        magnetometer?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL) }
    }

    fun stop() {
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent) {
        when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> latestAccel = event.values.copyOf()
            Sensor.TYPE_GYROSCOPE -> latestGyro = event.values.copyOf()
            // TODO: route magnetometer readings only through the gated
            // heading-at-standstill path (see NavigationEngine), never here directly.
        }
        val a = latestAccel
        val g = latestGyro
        if (a != null && g != null) {
            onSample?.invoke(
                ImuSample(
                    elapsedRealtimeNanos = SystemClock.elapsedRealtimeNanos(),
                    accelX = a[0], accelY = a[1], accelZ = a[2],
                    gyroX = g[0], gyroY = g[1], gyroZ = g[2],
                )
            )
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        // TODO: flag degraded sensor accuracy (e.g. SENSOR_STATUS_UNRELIABLE)
        // to NavigationEngine so it can widen the confidence radius.
    }
}
