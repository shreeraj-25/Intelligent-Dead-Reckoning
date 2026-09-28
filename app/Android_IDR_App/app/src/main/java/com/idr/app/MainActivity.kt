package com.idr.app

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

/**
 * Entry point. Wires SensorRepository + LocationRepository into the
 * NavigationEngine and renders MapScreen. Sensor/GNSS permission requests
 * happen here before any repository starts streaming.
 *
 * TODO: request ACCESS_FINE_LOCATION + HIGH_SAMPLING_RATE_SENSORS at runtime
 * TODO: instantiate SensorRepository, LocationRepository, NavigationEngine
 * TODO: bind NavigationEngine output to MapScreen's vehicle marker + confidence overlay
 */
class MainActivity : AppCompatActivity() {

    private lateinit var sensorRepository: SensorRepository
    private lateinit var locationRepository: LocationRepository
    private lateinit var navigationEngine: NavigationEngine

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sensorRepository = SensorRepository(this)
        locationRepository = LocationRepository(this)
        navigationEngine = NavigationEngine()

        // TODO: navigationEngine.attach(sensorRepository, locationRepository)
        // TODO: navigationEngine.observe { state -> mapScreen.render(state) }
    }
}
