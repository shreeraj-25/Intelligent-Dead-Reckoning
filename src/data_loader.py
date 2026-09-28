"""Flexible CSV loader for the common IDR schema."""
from pathlib import Path
import pandas as pd

ALIASES={
 'timestamp':['timestamp','time','time_s','timestamp_s','ts'],
 'accel_x':['accel_x','ax','accelerometer_x'], 'accel_y':['accel_y','ay','accelerometer_y'], 'accel_z':['accel_z','az','accelerometer_z'],
 'gyro_x':['gyro_x','gx','gyroscope_x'], 'gyro_y':['gyro_y','gy','gyroscope_y'], 'gyro_z':['gyro_z','gz','gyroscope_z'],
 'mag_x':['mag_x','mx','magnetometer_x'], 'mag_y':['mag_y','my','magnetometer_y'], 'mag_z':['mag_z','mz','magnetometer_z'],
 'gnss_lat':['gnss_lat','latitude','lat'], 'gnss_lon':['gnss_lon','longitude','lon'], 'gnss_speed':['gnss_speed','speed'], 'gnss_bearing':['gnss_bearing','bearing','course'], 'gnss_accuracy':['gnss_accuracy','accuracy','horizontal_accuracy']}

def _normalize(df):
    rename={}
    lower={c.lower().strip():c for c in df.columns}
    for target,names in ALIASES.items():
        for n in names:
            if n in lower: rename[lower[n]]=target; break
    out=df.rename(columns=rename).copy()
    if 'timestamp' not in out: raise ValueError('No timestamp column found')
    out=out.loc[:,~out.columns.duplicated()]
    out['timestamp']=pd.to_numeric(out['timestamp'],errors='ignore')
    return out

def list_io_vnbd_sequences(root):
    p=Path(root)
    if not p.exists(): return []
    files=sorted([x for x in p.rglob('*') if x.is_file() and x.suffix.lower() in {'.csv','.parquet','.feather'}])
    return [str(x) for x in files]

def load_sequence(sequence_path):
    p=Path(sequence_path)
    if p.is_dir():
        candidates=list(p.glob('*.csv'))
        if not candidates: raise FileNotFoundError(f'No CSV files in {p}')
        p=candidates[0]
    if p.suffix.lower()=='.csv': df=pd.read_csv(p)
    elif p.suffix.lower()=='.parquet': df=pd.read_parquet(p)
    elif p.suffix.lower()=='.feather': df=pd.read_feather(p)
    else: raise ValueError(f'Unsupported file type: {p.suffix}')
    return _normalize(df)

def load_android_log(csv_path): return load_sequence(csv_path)
