import math
import pyglet as pg

from .signal    import Signal
from .resource  import Resources
from .base      import Drawable, Collider
from .physics   import RAYCAST_FILTER, COLLISION_MAP


class Weapon:

    def __init__(self, size, ammo=350, *args, **kwargs):
        self.ammo = ammo
        self.bullets = []
        self.batch = pg.graphics.Batch()

        self.muzzle_offset = (size[0]/2+Bullet.SIZE/2, -size[1]*.21)
        self.muzzle_mag = math.hypot(*self.muzzle_offset) + 4
        self.muzzle_angle = angle(self.muzzle_offset)

        self.on_fire = Signal("on_fire")
        self.on_fire.connect(self._fire)

    def _fire(self, position, rotation, direction, collision, physics):
        # -- check ammo and decrement
        if self.ammo <= 0: return
        self.ammo -= 1

        # -- eject bullet
        px, py = position
        angle = self.muzzle_angle - rotation
        dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        px += dx * self.muzzle_mag
        py += dy * self.muzzle_mag

        b = Bullet(direction, position=(px, py), batch=self.batch,
                    physics=physics,
                    collision_type=collision,
                    collision_filter=pm.ShapeFilter(categories=RAYCAST_FILTER))

        b.on_collision_enter.connect(lambda *args : self.bullets.remove(b))
        self.bullets.append(b)

    def draw(self):
        self.batch.draw()

    def update(self, dt):
        for bullet in self.bullets:
            bullet.update(dt)

class Bullet(Drawable, Collider):
    SIZE = 12

    def __init__(self, direction, *args, **kwargs):
        Drawable.__init__(self, image=Resources.instance.sprite("bullet"), *args, **kwargs)
        Collider.__init__(self, mass=1, moment=100, speed=500, *args, **kwargs)

        # -  movement
        dx, dy = direction
        self.set_velocity((dx*self.speed, dy*self.speed))
        self.rotation = math.degrees(-math.atan2(dy, dx))
        self.sprite.update(rotation=self.rotation)

        # - collision
        self.collide_with(COLLISION_MAP.get("WallType"))
        self.on_collision_enter.connect(self.on_collision)

    def on_collision(self, other, *args):
        arbiter, space, data = args
        if other == COLLISION_MAP.get("WallType"):
            self.destroy()

    def update(self, dt):
        Drawable.update(self, dt)
        Collider.update(self, dt)

    def destroy(self):
        Drawable.destroy(self)
        Collider.destroy(self)

