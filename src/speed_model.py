"""CNN-GRU multi-task speed/motion model and regularizers."""
import torch
import torch.nn as nn
class IDRSpeedModel(nn.Module):
    def __init__(self,in_channels=9,num_motion_classes=5):
        super().__init__(); self.conv1=nn.Conv1d(in_channels,32,5,padding=2); self.conv2=nn.Conv1d(32,64,5,padding=2); self.gru=nn.GRU(64,64,batch_first=True); self.speed_mean_head=nn.Linear(64,1); self.speed_logvar_head=nn.Linear(64,1); self.motion_class_head=nn.Linear(64,num_motion_classes)
    def forward(self,x):
        if x.ndim!=3: raise ValueError('Expected input shape (batch,time,features)')
        x=torch.relu(self.conv1(x.permute(0,2,1))); x=torch.relu(self.conv2(x)); x=x.permute(0,2,1); _,h=self.gru(x); f=h[-1]
        return self.speed_mean_head(f), self.speed_logvar_head(f).clamp(-10,10), self.motion_class_head(f)

def heteroscedastic_speed_loss(speed_mean,speed_logvar,speed_true):
    precision=torch.exp(-speed_logvar.clamp(-10,10)); return (0.5*precision*(speed_true-speed_mean)**2+0.5*speed_logvar).mean()

def smoothness_penalty(speed_pred_sequence):
    x=speed_pred_sequence
    if x.shape[-1] != 1 and x.ndim==2: x=x.unsqueeze(-1)
    return ((x[:,1:]-x[:,:-1])**2).mean() if x.shape[1]>1 else x.new_zeros(())

def jerk_penalty(accel_sequence):
    x=accel_sequence
    if x.shape[1]<=2: return x.new_zeros(())
    return ((x[:,2:]-2*x[:,1:-1]+x[:,:-2])**2).mean()
