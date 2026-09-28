"""Practical 2-D GNSS/IMU extended Kalman filter for local vehicle navigation."""
import numpy as np

class DeadReckoningEKF:
    # x = [east, north, v_east, v_north, heading, accel_bias_forward, gyro_bias_z]
    def __init__(self, initial_state, initial_covariance):
        self.x = np.asarray(initial_state, dtype=float).reshape(7).copy()
        self.P = np.asarray(initial_covariance, dtype=float).reshape(7,7).copy()
        self.P = (self.P+self.P.T)/2

    def predict(self, accel_forward, gyro_z, dt):
        dt = float(dt)
        if dt <= 0 or dt > 5: raise ValueError("dt must be in (0, 5]")
        a = float(accel_forward) - self.x[5]
        wz = float(gyro_z) - self.x[6]
        th = self.x[4]
        c,s=np.cos(th),np.sin(th)
        # Forward acceleration projected to ENU.
        ae,an=a*c,a*s
        self.x[0] += self.x[2]*dt + 0.5*ae*dt*dt
        self.x[1] += self.x[3]*dt + 0.5*an*dt*dt
        self.x[2] += ae*dt; self.x[3] += an*dt; self.x[4] += wz*dt
        self.x[4] = (self.x[4]+np.pi)%(2*np.pi)-np.pi
        F=np.eye(7)
        F[0,2]=dt; F[1,3]=dt
        F[0,4]=-0.5*a*s*dt*dt; F[1,4]=0.5*a*c*dt*dt
        F[2,4]=-a*s*dt; F[3,4]=a*c*dt
        F[0,5]=-0.5*c*dt*dt; F[1,5]=-0.5*s*dt*dt
        F[2,5]=-c*dt; F[3,5]=-s*dt; F[4,6]=-dt
        q=np.diag([0.01,0.01,0.1,0.1,0.02,0.001,0.001])
        self.P=F@self.P@F.T+q*dt
        self.P=(self.P+self.P.T)/2
        return self.x.copy()

    def _update(self, z, h, H, R, gate=9.21):
        z=np.atleast_1d(np.asarray(z,float)); h=np.atleast_1d(np.asarray(h,float)); H=np.atleast_2d(np.asarray(H,float)); R=np.atleast_2d(np.asarray(R,float))
        y=z-h; S=H@self.P@H.T+R
        try: nis=float(y.T@np.linalg.solve(S,y))
        except np.linalg.LinAlgError: return False
        if nis>gate: return False
        K=self.P@H.T@np.linalg.pinv(S); self.x += K@y
        I=np.eye(7); self.P=(I-K@H)@self.P@(I-K@H).T+K@R@K.T; self.P=(self.P+self.P.T)/2
        return True

    def correct_gnss(self, gnss_position, gnss_speed=None, R_gnss=None):
        pos=np.asarray(gnss_position,float).reshape(2)
        if R_gnss is None: R_gnss=np.diag([9.,9.,1.])
        R=np.asarray(R_gnss,float)
        h=self.x[[0,1]]; H=np.zeros((2,7)); H[0,0]=H[1,1]=1
        if gnss_speed is None or R.shape==(2,2): return self._update(pos,h,H,R)
        speed=float(gnss_speed); th=self.x[4]; pred=np.hypot(self.x[2],self.x[3])
        Hs=np.zeros((1,7));
        if pred>1e-6: Hs[0,2]=self.x[2]/pred; Hs[0,3]=self.x[3]/pred
        return self._update(np.r_[pos,speed], np.r_[h,pred], np.vstack([H,Hs]), R)

    def correct_ai_speed(self, predicted_speed, predicted_variance):
        speed=max(0.,float(predicted_speed)); var=max(float(predicted_variance),1e-4)
        pred=np.hypot(self.x[2],self.x[3]); H=np.zeros((1,7));
        if pred>1e-6: H[0,2]=self.x[2]/pred; H[0,3]=self.x[3]/pred
        return self._update([speed],[pred],H,[[var]])

    def correct_zupt(self):
        H=np.zeros((2,7)); H[0,2]=H[1,3]=1
        return self._update([0.,0.], self.x[[2,3]], H, np.diag([0.03,0.03]))

    def correct_non_holonomic(self, weight=1.0):
        # Lateral velocity relative to heading should be near zero.
        w=float(np.clip(weight,0.,1.)); th=self.x[4]; c,s=np.cos(th),np.sin(th)
        lateral=-s*self.x[2]+c*self.x[3]
        H=np.zeros((1,7)); H[0,2]=-s; H[0,3]=c
        return self._update([0.],[lateral],H,[[max(0.01,1./max(w,1e-3))]])
