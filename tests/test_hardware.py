from motionforge.system.hardware import detect_hardware
def test_hardware():
 h=detect_hardware(); assert h.cpu_threads>=1 and h.ram_gb>0 and h.backend in {"cpu","cuda"}
