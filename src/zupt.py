import numpy as np
from . import config

def is_stationary(gyro_window, accel_window, predicted_speed):
    g=np.asarray(gyro_window,float); a=np.asarray(accel_window,float)
    if g.size==0 or a.size==0: return False
    gyro_mag=np.linalg.norm(g,axis=1) if g.ndim>1 else np.abs(g)
    accel_var=float(np.var(a,axis=0).mean()) if a.ndim>1 else float(np.var(a))
    return bool(np.mean(gyro_mag)<=config.ZUPT_GYRO_THRESH and accel_var<=config.ZUPT_ACCEL_VAR_THRESH and float(predicted_speed)<=config.ZUPT_SPEED_THRESH)
