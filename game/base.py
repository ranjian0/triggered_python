import pyglet as pg
import pymunk as pm

from .signal import Signal
from .core import (
    image_set_size,
    image_set_anchor_center)

class Object:

    def __init__(self, size=(1,1), position=(0, 0),  rotation=0, *args, **kwargs):
        self.size = size
        self.position = position
        self.rotation = rotation

    def _get_x(self):
        return self.position[0]
    def _set_x(self, val):
        self.position = (val, self.position[1])
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self.position[1]
    def _set_y(self, val):
        self.position = (self.position[0], val)
    y = property(_get_y, _set_y)

    def _get_width(self):
        return self.size[0]
    def _set_width(self, val):
        self.size = (val, self.size[1])
    width = property(_get_width, _set_width)

    def _get_height(self):
        return self.size[1]
    def _set_height(self, val):
        self.size = (self.size[0], val)
    height = property(_get_height, _set_height)

    def destroy(self):
        del self.size
        del self.position
        del self.rotation

class Drawable(Object):

    def __init__(self, image=None, batch=None, *args, **kwargs):
        super(Drawable, self).__init__(*args, **kwargs)
        self.batch = batch or pg.graphics.Batch()

        self.image = image
        image_set_size(self.image, *self.size)
        image_set_anchor_center(self.image)

        self.sprite = pg.sprite.Sprite(self.image, x=self.x, y=self.y, batch=self.batch)

    def draw(self):
        self.batch.draw()

    def update(self, dt):
        self.sprite.set_position(self.x, self.y)
        self.sprite.update(rotation=self.rotation)

    def destroy(self):
        super(Drawable, self).destroy()
        self.sprite.delete()
        del self.image
        del self.sprite

class PhysicsObject(Object):

    def __init__(self, physics=None, mass=1, moment=0, body_type=pm.Body.DYNAMIC,
                    speed=0, velocity=(0, 0), *args, **kwargs):
        super(PhysicsObject, self).__init__(*args, **kwargs)

        self.speed = speed
        self.physics = physics
        self.velocity = velocity

        self.body = pm.Body(mass, moment, body_type)
        self.body.position = self.position
        self.shape = pm.Circle(self.body, min(*self.size)*.45)
        self.physics.add(self.body, self.shape)

    def set_speed(self, val):
        self.speed = val

    def set_velocity(self, val):
        self.velocity = val

    def update(self, dt):
        px, py = self.position
        vx, vy = self.velocity

        px += vx * dt
        py += vy * dt

        self.position = (px, py)
        self.body.position = self.position
        self.physics.space.reindex_shapes_for_body(self.body)

    def destroy(self):
        super(PhysicsObject, self).destroy()
        self.physics.remove(self.body, self.shape)
        del self.speed
        del self.velocity
        del self.body
        del self.shape

class Collider(PhysicsObject):

    def __init__(self, collision_type=None, collision_filter=None, *args, **kwargs):
        super(Collider, self).__init__(*args, **kwargs)
        self.on_collision_enter = Signal("on_collision_enter")
        self.on_collision_exit = Signal("on_collision_exit")

        if collision_type:
            self.set_collision_type(collision_type)
        if collision_filter:
            self.set_collision_filter(collision_filter)

    def set_collision_type(self, col_type):
        self.shape.collision_type = col_type

    def set_collision_filter(self, col_flt):
        self.shape.filter = col_flt

    def collide_with(self, _type):
        self.physics.add_collision_handler(
                self.shape.collision_type,
                _type,
                handler_begin = lambda *col_args: self._on_col_enter(_type, *col_args),
                handler_separate = lambda *col_args: self._on_col_exit(_type, *col_args)
            )

    def _on_col_enter(self, other, *args):
        self.on_collision_enter(other, *args)
        return True

    def _on_col_exit(self, other, *args):
        self.on_collision_exit(other, *args)
        return True

class Entity(Drawable, Collider):

    def __init__(self, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)

        # -- health properties
        self.dead = False
        self.health = 100
        self.damage = 5
        self.max_health = 100

        self.on_damage = Signal("on_entity_damage")
        self.on_damage.connect(self._damage)

    def _damage(self):
        self.health = max(0, self.health-self.damage)
        if self.health <= 0:
            self.dead = True

    def draw(self):
        super(Entity, self).draw()

    def update(self, dt):
        super(Entity, self).update(dt)

    def destroy(self):
        super(Entity, self).destroy()

        del self.dead
        del self.health
        del self.damage
        del self.max_health
        del self.on_damage

