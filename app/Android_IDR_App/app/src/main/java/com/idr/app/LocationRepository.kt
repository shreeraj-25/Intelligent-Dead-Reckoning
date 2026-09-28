package com.idr.app

import android.annotation.SuppressLint
import android.content.Context
import android.location.GnssStatus
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.os.SystemClock

/**
 * Deliberately uses raw android.location.LocationManager with GPS_PROVIDER
 * plus GnssStatus, NOT FusedLocationProviderClient. FusedLocationProviderClient
 * applies Google's own smoothing/fusion before handing back a location, which
 * would mean double-filtering once fed into our own EKF (see docs/methodology.md
 * Fix 1). This repository exposes true raw fixes and real signal-quality
 * metrics (satellite count, per-satellite Cn0) for src/gnss_quality.py-equivalent
 * on-device trust scoring.
 */
class LocationRepository(private val context: Context) {

    data class RawFix(
        val elapsedRealtimeNanos: Long,
        val latitude: Double, val longitude: Double,
        val speedMps: Float, val bearingDeg: Float, val accuracyM: Float,
        val satelliteCount: Int, val meanCn0DbHz: Float,
    )

    private val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    private var satelliteCount = 0
    private var meanCn0 = 0f

    private val gnssStatusCallback = object : GnssStatus.Callback() {
        override fun onSatelliteStatusChanged(status: GnssStatus) {
            satelliteCount = status.satelliteCount
            var sum = 0f
            for (i in 0 until status.satelliteCount) sum += status.getCn0DbHz(i)
            meanCn0 = if (status.satelliteCount > 0) sum / status.satelliteCount else 0f
            // TODO: feed (satelliteCount, meanCn0) into a gnss_quality.quality_score-
            // equivalent trust function shared with the adaptive EKF.
        }
    }

    @SuppressLint("MissingPermission") // caller is responsible for the runtime permission check
    fun start(onFix: (RawFix) -> Unit) {
        locationManager.registerGnssStatusCallback(gnssStatusCallback, null)

        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                onFix(
                    RawFix(
                        elapsedRealtimeNanos = SystemClock.elapsedRealtimeNanos(),
                        latitude = location.latitude,
                        longitude = location.longitude,
                        speedMps = if (location.hasSpeed()) location.speed else Float.NaN,
                        bearingDeg = if (location.hasBearing()) location.bearing else Float.NaN,
                        accuracyM = if (location.hasAccuracy()) location.accuracy else Float.NaN,
                        satelliteCount = satelliteCount,
                        meanCn0DbHz = meanCn0,
                    )
                )
            }

            @Deprecated("Deprecated in Java")
            override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
            override fun onProviderEnabled(provider: String) {}
            override fun onProviderDisabled(provider: String) {}
        }

        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            /* minTimeMs = */ 0L,
            /* minDistanceM = */ 0f,
            listener,
        )
        // TODO: also register a GnssMeasurementsEvent.Callback for raw
        // pseudorange/carrier data if finer-grained signal quality is needed.
    }

    fun stop() {
        locationManager.unregisterGnssStatusCallback(gnssStatusCallback)
        // TODO: keep a reference to the LocationListener to unregister it here too.
    }
}
