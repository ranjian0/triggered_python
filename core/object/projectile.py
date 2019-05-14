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
import pymunk as pm
import pyglet as pg
from resources import Resources
from core.math import Vec2
from core.collection import Collection
from core.physics import PhysicsWorld, PhysicsBody
from core.utils import image_set_size, image_set_anchor_center


def ProjectileCollection():
    return Collection(Projectile)


class Projectile:
    SIZE = (15, 15)
    SPEED = 400

    def __init__(self, position, direction, batch, tag=""):
        self.batch = batch
        self.direction = direction
        self.destroyed = False

        # -- sprite
        self.image = Resources.instance.sprite("bullet")
        image_set_size(self.image, *self.SIZE)
        image_set_anchor_center(self.image)
        self.sprite = pg.sprite.Sprite(self.image, *position, batch=self.batch)

        # -- physics
        physics = PhysicsWorld.instance
        self.body = PhysicsBody(1, pm.moment_for_box(1, self.SIZE))
        self.shape = pm.Poly.create_box(self.body, self.SIZE, radius=0.6)
        self.shape.filter = pm.ShapeFilter(categories=0x1)

        self.body.tag = tag
        self.body.position = position
        physics.add(self.body, self.shape)
        physics.register_collision(
            self.shape.collision_type, self.on_collision_enter, lambda other: None
        )

    def on_collision_enter(self, other):
        # XXX Unwanted Behaviour: called for sensors shapes
        for shape in other.shapes:
            if shape.sensor:
                continue

            res = shape.shapes_collide(self.shape)
            if res.points and not self.destroyed:
                self.destroy()

    def on_update(self, dt):
        self.body.velocity = self.direction * self.SPEED * dt
        self.body.angle = self.direction.angle
        if self.sprite.image:
            # pyglet rotates clockwise (pymunk anti-clockwise)
            self.sprite.update(*self.body.position, -math.degrees(self.direction.angle))

    def destroy(self):
        PhysicsWorld.remove(self.body, self.shape)
        self.sprite.delete()
        self.destroyed = True
