from __future__ import annotations
from .trajectory import Keyframe, Trajectory

def interpolate_trajectory(traj: Trajectory, num_frames: int) -> list[Keyframe]:
    if num_frames <= 0 or not traj.keyframes:
        return []
    src = sorted(traj.keyframes, key=lambda k: k.frame)
    out: list[Keyframe] = []
    for frame in range(num_frames):
        if frame <= src[0].frame:
            out.append(Keyframe(frame=frame, x=src[0].x, y=src[0].y)); continue
        if frame >= src[-1].frame:
            out.append(Keyframe(frame=frame, x=src[-1].x, y=src[-1].y)); continue
        left, right = src[0], src[-1]
        for a, b in zip(src, src[1:]):
            if a.frame <= frame <= b.frame:
                left, right = a, b; break
        t = (frame - left.frame) / max(1, right.frame - left.frame)
        out.append(Keyframe(frame=frame, x=left.x + (right.x-left.x)*t, y=left.y + (right.y-left.y)*t))
    return out
