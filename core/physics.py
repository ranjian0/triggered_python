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

import pymunk as pm
import itertools as it
from pymunk import pyglet_util as putils

DEBUG = 0
PHYSICS_STEPS = 60

class PhysicsWorld:

    # -- singleton
    instance = None
    def __new__(cls):
        if PhysicsWorld.instance is None:
            PhysicsWorld.instance = object.__new__(cls)
        return PhysicsWorld.instance

    def __init__(self):
        self.space = pm.Space()
        self.collision_type = it.count()

    def add(self, *args):
        for obj in args:
            if isinstance(obj, pm.Shape):
                obj.collision_type = next(self.collision_type)
        self.space.add(*args)

    def remove(self, *args):
        self.space.remove(*args)

    def clear(self):
        self.remove(self.space.static_body.shapes)
        for body in self.space.bodies:
            self.remove(body, body.shapes)

    def on_update(self, dt):
        for _ in it.repeat(None, PHYSICS_STEPS):
            self.space.step(1. / PHYSICS_STEPS)

    def register_collision(self, _type, on_enter, on_exit):
        handler = self.space.add_wildcard_collision_handler(_type)

        def handler_begin(arbiter, space, data):
            this, other = arbiter.shapes
            on_enter(other.body)
            return True
        handler.begin = handler_begin

        def handler_separate(arbiter, space, data):
            this, other = arbiter.shapes
            on_exit(other.body)
        handler.separate = handler_separate

    def on_draw(self):
        if DEBUG:
            options = putils.DrawOptions()
            self.space.debug_draw(options)

    def reindex(self, b):
        self.space.reindex_shapes_for_body(b)

class PhysicsBody(pm.Body):
    """ Convinience class for tagging physics bodies """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tag = ""

    def _get_tag(self):
        return self._tag
    def _set_tag(self, name):
        self._tag = name
    tag = property(_get_tag, _set_tag)