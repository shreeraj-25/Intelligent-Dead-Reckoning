import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def plot_trajectory_comparison(ground_truth,raw_dr,ekf,adaptive_ekf,save_path=None):
    fig,ax=plt.subplots(figsize=(8,6))
    for arr,label in [(ground_truth,'Ground truth'),(raw_dr,'Raw DR'),(ekf,'EKF'),(adaptive_ekf,'Adaptive EKF')]:
        a=np.asarray(arr); ax.plot(a[:,0],a[:,1],label=label)
    ax.set_xlabel('East (m)'); ax.set_ylabel('North (m)'); ax.set_title('Trajectory comparison'); ax.axis('equal'); ax.grid(True); ax.legend(); fig.tight_layout()
    if save_path: Path(save_path).parent.mkdir(parents=True,exist_ok=True); fig.savefig(save_path,dpi=160); plt.close(fig)
    return fig,ax

def plot_outage_drift(times_s,drift_m,outage_start_s,outage_end_s,save_path=None):
    fig,ax=plt.subplots(figsize=(8,4)); ax.plot(times_s,drift_m); ax.axvspan(outage_start_s,outage_end_s,alpha=.2); ax.set(xlabel='Time (s)',ylabel='Drift (m)',title='GNSS outage drift'); ax.grid(True); fig.tight_layout()
    if save_path: Path(save_path).parent.mkdir(parents=True,exist_ok=True); fig.savefig(save_path,dpi=160); plt.close(fig)
    return fig,ax

def export_for_dashboard(trajectory_data,out_path):
    p=Path(out_path); p.parent.mkdir(parents=True,exist_ok=True)
    def clean(v):
        if isinstance(v,np.ndarray): return v.tolist()
        if isinstance(v,(np.floating,np.integer)): return v.item()
        if isinstance(v,dict): return {k:clean(x) for k,x in v.items()}
        if isinstance(v,(list,tuple)): return [clean(x) for x in v]
        return v
    with p.open('w',encoding='utf-8') as f: json.dump(clean(trajectory_data),f,indent=2,allow_nan=False)
    return str(p)
