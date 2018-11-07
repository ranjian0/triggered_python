import pymunk as pm
import itertools as it
from pymunk import pyglet_util as putils

from .settings import FPS

RAYCAST_FILTER = 0x1
RAYCAST_MASK = pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS ^ RAYCAST_FILTER)
COLLISION_MAP = {
    "PlayerType"        : 1,
    "WallType"          : 2,
    "PlayerBulletType"  : 3,
    "EnemyBulletType"   : 4,
    "EnemyType"         : 100
}


class Physics:

    def __init__(self):
        self.space = pm.Space()

    def add(self, *args):
        self.space.add(*args)

    def remove(self, *args):
        self.space.remove(*args)

    def clear(self):
        self.remove(self.space.static_body.shapes)
        for body in self.space.bodies:
            self.remove(body, body.shapes)

    def update(self, dt):
        for _ in it.repeat(None, FPS):
            self.space.step(1. / FPS)

    def raycast(self, start, end, radius, filter):
        res = self.space.segment_query_first(start, end, radius, filter)
        return res

    def add_collision_handler(self, type_a, type_b,
        handler_begin=None, handler_pre=None, handler_post=None,
        handler_separate=None, data=None):

        handler = self.space.add_collision_handler(type_a, type_b)
        if data:
            handler.data.update(data)

        if handler_begin:
            handler.begin = handler_begin
        if handler_pre:
            handler.pre_solve = handler_pre
        if handler_post:
            handler.post_solve = handler_post
        if handler_separate:
            handler.separate = handler_separate

        return handler

    def debug_draw(self):
        options = putils.DrawOptions()
        self.space.debug_draw(options)

