"""Adaptive covariance logic for the EKF."""
import numpy as np

def compute_process_noise(base_Q, vibration_score, outage_duration_s):
    q=np.asarray(base_Q,float).copy(); vib=np.clip(float(vibration_score),0,1); outage=max(0.,float(outage_duration_s))
    factor=1.0 + 4.0*vib + min(10.0, outage/15.0)
    return q*factor

def compute_gnss_measurement_noise(base_R, gnss_accuracy_m, satellite_count):
    r=np.asarray(base_R,float).copy(); acc=max(float(gnss_accuracy_m),0.5); sats=max(int(satellite_count),1)
    factor=(acc/5.0)**2 * (8.0/max(sats,4))
    return r*max(0.25,min(25.0,factor))

def gnss_mode(gnss_accuracy_m, seconds_since_last_fix):
    t=float(seconds_since_last_fix); acc=None if gnss_accuracy_m is None else float(gnss_accuracy_m)
    if t>=10.: return 'blackout'
    if t>=2.: return 'recovery'
    if acc is None: return 'poor'
    return 'good' if acc<=10.0 else 'poor'
