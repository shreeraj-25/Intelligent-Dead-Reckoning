import numpy as np
import pandas as pd

def positional_drift_percent(estimated_trajectory, ground_truth_trajectory, distance_travelled_m):
    e=np.asarray(estimated_trajectory,float); g=np.asarray(ground_truth_trajectory,float)
    if len(e)==0 or len(g)==0: raise ValueError("trajectories cannot be empty")
    err=np.linalg.norm(e[-1]-g[-1]); d=float(distance_travelled_m)
    return float(np.nan if d<=0 else 100*err/d)

def rmse(estimated, ground_truth):
    e=np.asarray(estimated,float); g=np.asarray(ground_truth,float)
    if e.shape!=g.shape: raise ValueError("estimated and ground_truth must have the same shape")
    return float(np.sqrt(np.mean((e-g)**2)))

def speed_mae(predicted_speed,true_speed):
    p=np.asarray(predicted_speed,float); t=np.asarray(true_speed,float)
    if p.shape!=t.shape: raise ValueError("predicted_speed and true_speed must have the same shape")
    return float(np.mean(np.abs(p-t)))

def build_ablation_table(results):
    rows=[]
    for name,vals in results.items(): rows.append({'configuration':name,'drift_30s':vals.get('drift_30s',np.nan),'drift_60s':vals.get('drift_60s',np.nan),'rmse':vals.get('rmse',np.nan)})
    return pd.DataFrame(rows,columns=['configuration','drift_30s','drift_60s','rmse'])
