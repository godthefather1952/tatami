from motionforge.config.settings import PRESETS

def test_preset():
    p = PRESETS["CPU_SAFE"]
    assert p.width == 64
    assert p.height == 64
    assert p.num_frames == 4
    assert p.steps == 2
