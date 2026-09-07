import pytest
from pydantic import ValidationError
from motionforge.motion.trajectory import Trajectory,Keyframe
def test_normalized(): assert Trajectory(id='a',keyframes=[Keyframe(frame=0,x=.5,y=.2)]).keyframes[0].x==.5
def test_bounds():
 with pytest.raises(ValidationError): Keyframe(frame=0,x=2,y=.2)
