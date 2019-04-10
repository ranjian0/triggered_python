import math
import pyglet as pg
import pymunk as pm

from core.object import Map
from core.physics import PhysicsWorld, PhysicsBody
from core.utils import (
    reset_matrix,
    image_set_size,
    image_set_anchor_center)

class Entity(object):

    def __init__(self, **kwargs):
        self.speed  = 0.0
        self.radius = 30.0
        self.image  = None
        self.batch = pg.graphics.Batch()

        # -- health
        self.health = 100
        self.min_health = 0
        self.max_health = 100
        self.destroyed = False

        # -- collision
        mass = 100
        self.body = PhysicsBody(mass, pm.moment_for_circle(mass, 0, self.radius))
        self.shape = pm.Circle(self.body, self.radius)


        # -- LOAD PROPERTIES
        if 'image' in kwargs:
            self.image = kwargs.pop('image')
            image_set_size(self.image, self.radius*2, self.radius*2)
            image_set_anchor_center(self.image)

            self.sprite = pg.sprite.Sprite(self.image,
                *self.position, batch=self.batch)

        if 'minimap_image' in kwargs:
            self._show_minimap = False
            self._window_size = (0, 0)
            self.minimap_image = kwargs.pop('minimap_image')
            image_set_size(self.minimap_image, 25, 25)
            image_set_anchor_center(self.minimap_image)
            self.minimap_sprite = pg.sprite.Sprite(self.minimap_image)

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

    def on_draw_last(self):
        if self._show_minimap:
            with reset_matrix(*self._window_size):
                self.minimap_sprite.draw()

    def on_resize(self, w, h):
        self._window_size = (w, h)

    def on_update(self, dt):
        if self.sprite.image:
            # pyglet rotates clockwise (pymunk anti-clockwise)
            self.sprite.update(*self.position, -math.degrees(self.rotation))

        if self.minimap_sprite.image:
            mmap = Map.instance._minimap

            w, h = mmap.width, mmap.height
            offx, offy = mmap.x-w, mmap.y
            sx, sy = [mini/_map for mini, _map in zip((w,h), Map.instance.size)]
            px, py = self.position

            _x, _y = offx + (px*sx), offy + (py*sy)
            self.minimap_sprite.update(x=_x, y=_y)

    def on_key_press(self, symbol, mod):
        if symbol == pg.window.key.TAB:
            self._show_minimap = True

    def on_key_release(self, symbol, mod):
        if symbol == pg.window.key.TAB:
            self._show_minimap = False

    def damage(self, amount=5):
        self.health -= amount
        self.on_damage(self.health)
        if self.health <= self.min_health:
            self.destroy()

    def destroy(self):
        PhysicsWorld.remove(self.body, self.shape)
        self.sprite.delete()
        self.minimap_sprite.delete()
        self.destroyed = True

