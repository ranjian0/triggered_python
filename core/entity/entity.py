import math
import pyglet as pg
import pymunk as pm

from core.physics import PhysicsWorld, PhysicsBody
from core.utils import (image_set_size,
    image_set_anchor_center)

class Entity(object):

    def __init__(self, **kwargs):
        self.speed  = 0.0
        self.radius = 30.0
        self.image  = None
        self.batch = pg.graphics.Batch()

        # -- health
        self.dead = False
        self.health = 100
        self.min_health = 0
        self.max_health = 100

        # -- collision
        self.body = PhysicsBody(100, pm.inf)
        self.shape = pm.Circle(self.body, self.radius)


        # -- LOAD PROPERTIES
        if 'image' in kwargs:
            self.image = kwargs.pop('image')
            image_set_size(self.image, self.radius*2, self.radius*2)
            image_set_anchor_center(self.image)

            self.sprite = pg.sprite.Sprite(self.image,
                *self.position, batch=self.batch)

        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

        # setup physics
        physics = PhysicsWorld.instance
        physics.add(self.body, self.shape)
        physics.register_collision(self.shape.collision_type,
            self.on_collision_enter, self.on_collision_exit)

    def _get_position(self):
        return self.body.position
    def _set_position(self, pos):
        self.body.position = pos
        PhysicsWorld.instance.reindex(self.body)
    position = property(_get_position, _set_position)

    def _get_rotation(self):
        return self.body.angle
    def _set_rotation(self, ang):
        self.body.angle = ang
    rotation = property(_get_rotation, _set_rotation)

    def _get_velocity(self):
        return self.body.velocity
    def _set_velocity(self, vel):
        self.body.velocity = vel
    velocity = property(_get_velocity, _set_velocity)

    def on_collision_enter(self, other):
        pass

    def on_collision_exit(self, other):
        pass

    def on_damage(self, health):
        pass

    def on_draw(self):
        self.batch.draw()

    def on_update(self, dt):
        if self.sprite.image:
            self.sprite.update(*self.position, math.degrees(self.rotation))

    def damage(self, amount=5):
        self.health -= amount
        self.on_damage(self.health)
        if self.health <= self.min_health:
            self.dead = True
            self.destroy()

    def destroy(self):
        PhysicsWorld.remove(self.body, self.shape)
        self.sprite.delete()

