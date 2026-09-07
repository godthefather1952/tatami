from motionforge.system.backend import resource_tier
from motionforge.system.hardware import HardwareInfo
def test_cpu_safe():
 h=HardwareInfo(2,8,7,20,False,None,None,"cpu"); assert resource_tier(h)=="CPU_SAFE"
