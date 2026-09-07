from motionforge.config.settings import PRESETS
def test_preset():
 p=PRESETS['CPU_SAFE']; assert p.width==128 and p.steps==2
