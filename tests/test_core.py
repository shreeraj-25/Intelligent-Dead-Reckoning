import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
import numpy as np, pandas as pd, torch
from src.preprocess import resample_imu, latlon_to_enu
from src.filters import DeadReckoningEKF
from src.speed_model import IDRSpeedModel
from src.motion_classifier import extract_window_features
from src.metrics import rmse, speed_mae

def test_resample():
    t=np.array([0,.1,.21,.3]); n=len(t)
    df=pd.DataFrame({'timestamp':t,'accel_x':np.arange(n),'accel_y':0.,'accel_z':9.8,'gyro_x':0.,'gyro_y':0.,'gyro_z':0.})
    out=resample_imu(df,10); assert len(out)==4

def test_ekf_smoke():
    k=DeadReckoningEKF(np.zeros(7),np.eye(7)); k.predict(1,0,.1); assert np.isfinite(k.x).all(); assert k.correct_ai_speed(1,.2)

def test_model_shape():
    a,b,c=IDRSpeedModel()(torch.zeros(2,100,9)); assert a.shape==(2,1) and b.shape==(2,1) and c.shape==(2,5)

def test_features(): assert extract_window_features(np.zeros((5,3)),np.zeros((5,3))).shape==(5,9)

def test_metrics(): assert rmse(np.array([1,2]),np.array([1,4]))>0; assert speed_mae(np.array([1,2]),np.array([1,4]))==1
