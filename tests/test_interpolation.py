from motionforge.motion.trajectory import Trajectory,Keyframe
from motionforge.motion.interpolation import interpolate_trajectory
def test_linear():
 t=Trajectory(id='x',keyframes=[Keyframe(frame=0,x=0,y=0),Keyframe(frame=2,x=1,y=1)]); out=interpolate_trajectory(t,3); assert out[1].x==.5
