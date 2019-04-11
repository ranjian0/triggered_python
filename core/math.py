#  Copyright 2019 Ian Karanja <karanjaichungwa@gmail.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import math
import operator
import pymunk as pm
from collections import namedtuple

class Vec2(pm.vec2d.Vec2d):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_tuple(self, precision=4):
        return round(float(self.x), precision), round((self.y), precision)

class Rect(object):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    size = property(lambda self: (self.w, self.h))
    position = property(lambda self: (self.x, self.y))

    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.w}, {self.h})"

    def hit(self, x, y):
        return (self.x <= x <= self.w) and (self.y <= y <= self.h)


class Bounds(namedtuple('_Bounds', "left bottom right top")):
    pass

def clamp(x, _min, _max):
    return max(_min, min(_max, x))

def angle(p):
    nx, ny = normalize(p)
    return math.degrees(math.atan2(ny, nx))

def normalize(p):
    mag = math.hypot(*p)
    if mag:
        return (p[0] / mag, p[1] / mag)
    return p

def heuristic(a, b):
    return sum(map(abs, tsub(a, b)))

def dist_sqr(x, y):
    return sum(map(operator.pow, map(operator.sub, x, y), (2,2)))

def distance(x, y):
    return math.sqrt(dist_sqr(x, y))

def tadd(x, y):
    return tuple(map(operator.add, x, y))

def tsub(x, y):
    return tuple(map(operator.sub, x, y))

def tmul(x, y):
    return tuple(map(operator.mul, x, y))

def tdiv(x, y):
    return tuple(map(operator.truediv, x, y))
