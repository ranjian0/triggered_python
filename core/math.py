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

class Point(object):
    def __init__(self, *args):
        if len(args) == 2:
            self.x, self.y = args[0], args[1]
        elif len(args) == 1:
            self.x, self.y = args[0][0], args[0][1]
        else:
            self.x, self.y = 0, 0

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __getitem__(self, i):
        return (self.x, self.y)[i]

    def __iter__(self):
        def gen():
            for i in (self.x, self.y):
                yield i
        return gen()

    def __add__(self, other):
        return Point(self.x + other[0], self.y + other[1])

class Size(object):
    def __init__(self, *args):
        if len(args) == 2:
            self.w, self.h = args[0], args[1]
        elif len(args) == 1:
            self.w, self.h = args[0][0], args[0][1]
        else:
            self.w, self.h = 0, 0

    def __repr__(self):
        return f"Size({self.w}, {self.h})"

    def __getitem__(self, i):
        return (self.w, self.h)[i]

    def __iter__(self):
        def gen():
            for i in (self.w, self.h):
                yield i
        return gen()

    def hit_test(self, x, y):
        return (x >= 0 and x <= self.w) and (y >= 0 and y <= self.h)

    def __add__(self, other):
        return Size(self.w + other[0], self.h + other[1])

    def __truediv__(self, other):
        if isinstance(other, (float, int)):
            return Size(self.w/other, self.h/other)
        return self

class Rect(object):
    '''Fast and simple rectangular collision structure'''

    def __init__(self, x=0, y=0, w=0, h=0):
        '''Create a rectangle'''
        self.x, self.y = x, y
        self.w, self.h = w, h

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)

    def intersect(self, r):
        '''Compute the intersection of two rectangles'''
        if not self.collides(r):
            return Rect(0, 0, 0, 0)
        x, y = max(self.x, r.x), max(self.y, r.y)
        x2, y2 = min(self.x+self.w, r.x+r.w), min(self.y+self.h, r.y+r.h)
        n = Rect( x, y, x2 - x, y2 - y )
        return n

    def collides(self, r):
        '''Determine whether two rectangles collide'''
        if self.x+self.w < r.x or self.y+self.h < r.y or \
                self.x > r.x + r.w or self.y > r.y + r.h:
            return False
        return True

    def hit_test(self, x, y):
        '''Determine whether a point is inside the rectangle'''
        return (x >= self.x and x <= self.x + self.w) and (y >= self.y and y <= self.y + self.h)

    @property
    def min(self):
        return (self.x, self.y)

    @property
    def max(self):
        return (self.x + self.w, self.y + self.h)

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h))

    def __repr__(self):
        return 'Rect(%d %d %d %d)' % (self.x, self.y, self.w, self.h)

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
