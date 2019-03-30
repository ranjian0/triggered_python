import math
import pymunk as pm
from collections import namedtuple

Bounds = namedtuple('_Bounds',
    "left bottom right top")

class Vec2(pm.vec2d.Vec2d):
    def __init__(self, *args, **kwargs):
        pm.vec2d.Vec2d.__init__(self, *args, **kwargs)

    def to_tuple(self, precision=2):
        return (round(self.x, precision), round(self.y, precision))

def clamp(x, _min, _max):
    return max(_min, min(_max, x))

def angle(p):
    nx, ny = normalize(p)
    return math.degrees(math.atan2(ny, nx))

def normalize(p):
    mag = math.hypot(*p)
    if mag:
        x = p[0] / mag
        y = p[1] / mag
        return (x, y)
    return p
