"""Phone-to-vehicle frame alignment helpers."""
import numpy as np
from . import config

def estimate_static_pitch_roll(accel_window):
    a=np.mean(np.asarray(accel_window,float),axis=0); ax,ay,az=a
    pitch=np.arctan2(-ax,np.hypot(ay,az)); roll=np.arctan2(ay,az)
    return float(pitch),float(roll)

def estimate_yaw_from_gnss_track(gnss_positions, phone_heading):
    p=np.asarray(gnss_positions,float); h=np.asarray(phone_heading,float)
    if len(p)<2 or len(h)<2: raise ValueError("At least two samples are required")
    d=np.diff(p,axis=0); bearings=np.arctan2(d[:,1],d[:,0]); n=min(len(bearings),len(h)-1)
    # circular mean of bearing - phone heading; ignore near-zero GNSS steps.
    valid=np.linalg.norm(d[:n],axis=1)>1e-3
    if not np.any(valid): raise ValueError("GNSS track has no usable movement")
    delta=np.angle(np.exp(1j*(bearings[:n][valid]-h[1:n+1][valid])))
    return float(np.angle(np.mean(np.exp(1j*delta))))

def phone_to_vehicle_frame(accel, gyro, rotation_matrix):
    R=np.asarray(rotation_matrix,float).reshape(3,3); a=np.asarray(accel,float); g=np.asarray(gyro,float)
    return a@R.T, g@R.T

def check_mount_disturbance(accel_window, expected_gravity_dir):
    a=np.mean(np.asarray(accel_window,float),axis=0); a/=max(np.linalg.norm(a),1e-9)
    e=np.asarray(expected_gravity_dir,float); e/=max(np.linalg.norm(e),1e-9)
    return bool(np.arccos(np.clip(np.dot(a,e),-1,1)) > np.deg2rad(10))

def gated_magnetometer_heading(mag_reading, is_stationary):
    if not is_stationary: return None
    m=np.asarray(mag_reading,float).reshape(3); norm=np.linalg.norm(m)
    if not config.MAG_FIELD_MIN_UT<=norm<=config.MAG_FIELD_MAX_UT: return None
    return float(np.arctan2(m[1],m[0]))
