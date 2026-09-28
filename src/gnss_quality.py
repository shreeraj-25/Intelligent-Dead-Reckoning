"""GNSS quality scoring utilities."""
import numpy as np

def quality_score(satellite_count, mean_snr_db, accuracy_m):
    sats=np.clip(float(satellite_count)/12.,0,1); snr=np.clip((float(mean_snr_db)-15.)/25.,0,1); acc=np.exp(-max(float(accuracy_m),0.)/20.)
    return float(np.clip(0.35*sats+0.30*snr+0.35*acc,0,1))

def is_fix_trustworthy(quality, threshold=0.5): return bool(float(quality)>=float(threshold))
