import math
import pyglet as pg
from .entity import Entity


class Player(Entity):

    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        self.direction = (0, 0)
        self.body.tag = "Player"

    def on_update(self, dt):
        Entity.on_update(self, dt)
        dx, dy = self.direction
        self.velocity = (
            dx * self.speed * dt,
            dy * self.speed * dt)

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
        self.rotation = -math.atan2(
            y - py, x - px)

    def on_collision_enter(self, other):
        if hasattr(other, 'tag') and other.tag == 'Enemy':
            print("Hit Enemy")

