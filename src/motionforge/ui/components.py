from __future__ import annotations
from motionforge.motion.serialization import loads
from motionforge.motion.trajectory import Keyframe, Trajectory, TrajectorySet

def upsert_keyframe(raw, trajectory_id: str, frame: int, x: float, y: float):
    data = loads(raw)
    tid = (trajectory_id or "point_1").strip()
    target = next((t for t in data.trajectories if t.id == tid), None)
    if target is None:
        target = Trajectory(id=tid, keyframes=[]); data.trajectories.append(target)
    target.keyframes = [k for k in target.keyframes if k.frame != int(frame)]
    target.keyframes.append(Keyframe(frame=int(frame), x=float(x), y=float(y)))
    target.keyframes.sort(key=lambda k:k.frame)
    return data.model_dump()

def remove_keyframe(raw, trajectory_id: str, frame: int):
    data=loads(raw); tid=(trajectory_id or "").strip()
    for t in list(data.trajectories):
        if t.id==tid:
            t.keyframes=[k for k in t.keyframes if k.frame != int(frame)]
            if not t.keyframes: data.trajectories.remove(t)
    return data.model_dump()

def clear_trajectories():
    return TrajectorySet().model_dump()
