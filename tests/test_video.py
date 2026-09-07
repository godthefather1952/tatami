from PIL import Image
from motionforge.media.video import encode_mp4,probe_video
def test_video(tmp_path):
 p=encode_mp4([Image.new('RGB',(64,64),'red'),Image.new('RGB',(64,64),'blue')],tmp_path/'x.mp4',2); assert p.stat().st_size>0 and probe_video(p)['frames']>=2
