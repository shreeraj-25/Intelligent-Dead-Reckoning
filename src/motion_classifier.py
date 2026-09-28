import numpy as np
MOTION_CLASSES={0:'stationary',1:'normal_driving',2:'acceleration_braking',3:'turning',4:'high_vibration_pothole'}

def extract_window_features(accel, gyro):
    a=np.asarray(accel,float); g=np.asarray(gyro,float)
    if a.ndim!=2 or g.ndim!=2 or a.shape!=g.shape or a.shape[1]!=3: raise ValueError("accel and gyro must both have shape (N,3)")
    am=np.linalg.norm(a,axis=1); gm=np.linalg.norm(g,axis=1)
    jerk=np.vstack([np.zeros((1,3)),np.diff(a,axis=0)])
    jm=np.linalg.norm(jerk,axis=1)
    return np.column_stack([a,g,am,gm,jm])

def rule_based_motion_label(speed,yaw_rate,jerk):
    if float(speed)<0.3 and abs(float(yaw_rate))<0.05: return 0
    if float(jerk)>4.0: return 4
    if abs(float(yaw_rate))>0.25: return 3
    if abs(float(jerk))>1.5: return 2
    return 1
