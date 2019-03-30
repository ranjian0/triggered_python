import math
import pyglet as pg
import pymunk as pm
from .entity import Entity
from resources import Resources
from core.object import Projectile


class Player(Entity):

    def __init__(self, **kwargs):
        Entity.__init__(self, image=Resources.instance.sprite("hitman1_gun"), **kwargs)
        self.direction = (0, 0)
        self.body.tag = "Player"
        self.projectiles = []

    def on_update(self, dt):
        Entity.on_update(self, dt)
        dx, dy = self.direction
        self.velocity = (
            dx * self.speed * dt,
            dy * self.speed * dt)

        for p in self.projectiles:
            p.on_update(dt)

    def on_key_press(self, symbol, mod):
        dx, dy = self.direction
        if symbol == pg.window.key.W:
            dy = 1
        if symbol == pg.window.key.S:
            dy = -1
        if symbol == pg.window.key.A:
            dx = -1
        if symbol == pg.window.key.D:
            dx = 1
        self.direction = (dx, dy)

        if symbol == pg.window.key.SPACE:
            self.shoot()

    def on_key_release(self, symbol, mod):
        dx, dy = self.direction
        if symbol == pg.window.key.W:
            dy = 0
        if symbol == pg.window.key.S:
            dy = 0
        if symbol == pg.window.key.A:
            dx = 0
        if symbol == pg.window.key.D:
            dx = 0
        self.direction = (dx, dy)

    def on_mouse_motion(self, x, y, dx, dy):
        px, py = self.position
        self.rotation = math.atan2(
            y - py, x - px)

    def on_collision_enter(self, other):
        if hasattr(other, 'tag') and other.tag == 'Enemy':
            pass

    def shoot(self):
        dx, dy = math.cos(self.rotation), math.sin(self.rotation)
        pos = self.position + pm.vec2d.Vec2d(dx, dy)*(self.radius + max(Projectile.SIZE))
        p = Projectile(pos, (dx, dy), self.batch)
        p.body.tag = "PlayerBullet"
        self.projectiles.append(p)
