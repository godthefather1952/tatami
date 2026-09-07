from datetime import datetime
from motionforge.system.paths import output_paths
def test_output_path():
 v,j=output_paths(12,datetime(2026,9,7,10,45)); assert '2026-09-07' in str(v) and v.suffix=='.mp4' and j.suffix=='.json'
