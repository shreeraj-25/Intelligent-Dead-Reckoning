package com.idr.app

import android.content.Context
import java.io.File
import java.io.FileWriter

/**
 * Writes timestamped IMU + raw GNSS samples to CSV, matching the column
 * schema src/data_loader.py's ALIASES map expects (timestamp, accel_x/y/z,
 * gyro_x/y/z, gnss_lat, gnss_lon, gnss_speed, ...). Used from Week 1-2
 * onward to collect real-device recordings in parallel with IO-VNBD work
 * (see docs/methodology.md Fix 4), independent of whether NavigationEngine
 * is fully wired up yet.
 */
class LogWriter(context: Context, fileName: String) {
    private val file = File(context.getExternalFilesDir(null), fileName)
    private val writer = FileWriter(file, /* append = */ true)
    private var headerWritten = file.length() > 0

    fun logImu(sample: SensorRepository.ImuSample) {
        ensureHeader("timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z")
        writer.appendLine(
            "${sample.elapsedRealtimeNanos},${sample.accelX},${sample.accelY},${sample.accelZ}," +
                "${sample.gyroX},${sample.gyroY},${sample.gyroZ}"
        )
    }

    fun logGnss(fix: LocationRepository.RawFix) {
        // TODO: unify into a single interleaved CSV, or write to a separate
        // gnss.csv and align offline via src/preprocess.align_gnss_to_imu.
    }

    private fun ensureHeader(header: String) {
        if (!headerWritten) {
            writer.appendLine(header)
            headerWritten = true
        }
    }

    fun close() = writer.close()
}
