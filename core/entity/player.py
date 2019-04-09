import math
import pyglet as pg
import pymunk as pm
from .entity import Entity
from resources import Resources
from core.math import Vec2
from core.object import ProjectileCollection
from core.utils import global_position


class Player(Entity):

    def __init__(self, **kwargs):
        Entity.__init__(self, image=Resources.instance.sprite("hitman1_gun"), **kwargs)
        self.direction = (0, 0)
        self.body.tag = "Player"
        self.projectiles = ProjectileCollection()

        self.running = False
        self.run_speed = self.speed * 1.5

    def on_update(self, dt):
        Entity.on_update(self, dt)
        self.projectiles.on_update(dt)

        dx, dy = self.direction
        speed = self.run_speed if self.running else self.speed
        self.velocity = (
            dx * speed * dt,
            dy * speed * dt)

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

        if symbol == pg.window.key.LSHIFT:
            self.running = True

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

        if symbol == pg.window.key.LSHIFT:
            self.running = False

    def on_mouse_press(self, x, y, button, mod):
        if button == pg.window.mouse.LEFT:
            self.shoot()

    def on_mouse_motion(self, x, y, dx, dy):
        px, py = self.position
        mx, my = global_position(x, y)
        self.rotation = math.atan2(
            my - py, mx - px)

    def on_collision_enter(self, other):
        if hasattr(other, 'tag') and other.tag == 'Enemy':
            pass

    def shoot(self):
        """ Eject projectile """
        # -- set relative muzzle location
        muzzle_loc = Vec2(self.radius*1.5, -self.radius*.4)

        # -- calculate direction of (1.muzzle location), (2.player rotation)
        rotation = muzzle_loc.angle + self.rotation
        d_muzzle = Vec2(math.cos(rotation), math.sin(rotation))
        d_player = Vec2(math.cos(self.rotation), math.sin(self.rotation))

        # -- eject bullet
        pos = self.position + (d_muzzle * muzzle_loc.length)
        self.projectiles.add(pos, d_player, self.batch, tag="PlayerBullet")
