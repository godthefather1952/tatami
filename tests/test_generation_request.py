import pytest
from pydantic import ValidationError
from motionforge.inference.request import GenerationRequest
def test_request():
 r=GenerationRequest(prompt='x',image_path='a.png',seed=1,width=128,height=128,num_frames=4,fps=4,steps=2); assert r.prompt=='x'
def test_dims():
 with pytest.raises(ValidationError): GenerationRequest(prompt='x',image_path='a',seed=1,width=130,height=128,num_frames=4,fps=4,steps=2)
