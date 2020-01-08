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
import pyglet as pg
import pymunk as pm
from .entity import Entity
from resources import Resources
from core.math import Vec2
from core.object import ProjectileCollection
from core.utils import reset_matrix, image_set_size, global_position


class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            image=Resources.instance.sprite("hitman1_gun"),
            minimap_image=Resources.instance.sprite("minimap_player"),
            **kwargs,
        )
        self.speed = 200
        self.direction = (0, 0)
        self.body.tag = "Player"
        self.projectiles = ProjectileCollection()

        self.running = False
        self.run_speed = self.speed * 1.5

        # XXX HUD Elements
        self.hud_batch = pg.graphics.Batch()

        # Health Bar
        border = Resources.instance.sprite("health_bar_border")
        border.anchor_y = border.height
        self.border = pg.sprite.Sprite(border, batch=self.hud_batch)

        self.bar_im = Resources.instance.sprite("health_bar")
        self.bar_im.anchor_y = self.bar_im.height
        self.bar = pg.sprite.Sprite(self.bar_im, batch=self.hud_batch)
        self._update_healthbar_indicator()

        # Ammo Indicator
        self.ammo = 350
        self.ammo_h = 30
        self.ammo_im = Resources.instance.sprite("ammo_bullet")
        image_set_size(self.ammo_im, self.ammo_h // 3, self.ammo_h)
        self.ammo_im.anchor_y = self.ammo_im.height
        self.ammo_sprites = [
            pg.sprite.Sprite(self.ammo_im, batch=self.hud_batch)
            for _ in range(self.ammo // 100)
        ]

        self.ammo_text = pg.text.Label(
            f" X {self.ammo}",
            bold=True,
            font_size=12,
            color=(200, 200, 0, 255),
            batch=self.hud_batch,
            anchor_y="top",
            anchor_x="left",
        )
        self._update_ammo_indicator()

    def _update_healthbar_indicator(self):
        w, h = self._window_size
        self.border.update(x=10, y=h)
        self.bar.update(x=10, y=h)

    def _update_ammo_indicator(self):
        w, h = self._window_size
        px, py = 10, h - (self.ammo_h * 1.5)

        # Sprites
        offx = self.ammo_im.width + 2
        for idx, sp in enumerate(self.ammo_sprites):
            sp.x = px + (idx * offx)
            sp.y = py

        # Text
        txt_off = px + (len(self.ammo_sprites) * offx)
        self.ammo_text.x = txt_off
        self.ammo_text.y = py

    def on_damage(self, health_percent):
        region = self.bar_im.get_region(
            0, 0, int(self.bar_im.width * health_percent), self.bar_im.height
        )
        region.anchor_y = self.bar_im.height
        self.bar.image = region

    def on_resize(self, w, h):
        super().on_resize(w, h)
        self._update_ammo_indicator()
        self._update_healthbar_indicator()

    def on_draw(self):
        super().on_draw()
        with reset_matrix(*self._window_size):
            self.hud_batch.draw()

    def on_update(self, dt):
        super().on_update(dt)

        self.projectiles.on_update(dt)

        dx, dy = self.direction
        speed = self.run_speed if self.running else self.speed
        self.velocity = (dx * speed * dt, dy * speed * dt)

    def on_key_press(self, symbol, mod):
        super().on_key_press(symbol, mod)

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
        super().on_key_release(symbol, mod)

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
            if self.ammo <= 0:
                return
            self.ammo -= 1

            # -- update ammo indicator
            num_bul = self.ammo // 100
            if len(self.ammo_sprites) > num_bul:
                self.ammo_sprites.pop()
            self.ammo_text.text = f" X {self.ammo}"
            self._update_ammo_indicator()

            self.shoot()

    def on_mouse_motion(self, x, y, dx, dy):
        px, py = self.position
        mx, my = global_position(x, y)
        self.rotation = math.atan2(my - py, mx - px)

    def on_collision_enter(self, other):
        super().on_collision_enter(other)

        if hasattr(other, "tag") and other.tag == "Enemy":
            pass

        if hasattr(other, "tag") and other.tag == "EnemyBullet":
            self.damage()

    def shoot(self):
        """ Eject projectile """
        # -- set relative muzzle location
        muzzle_loc = Vec2(self.radius * 1.5, -self.radius * 0.4)

        # -- calculate direction of (1.muzzle location), (2.player rotation)
        rotation = muzzle_loc.angle + self.rotation
        d_muzzle = Vec2(math.cos(rotation), math.sin(rotation))
        d_player = Vec2(math.cos(self.rotation), math.sin(self.rotation))

        # -- eject bullet
        pos = self.position + (d_muzzle * muzzle_loc.length)
        self.projectiles.add(pos, d_player, self.batch, tag="PlayerBullet")

    def destroy(self):
        super().destroy()
        self.border.delete()
        self.bar.delete()
        self.ammo_text.delete()
        for sp in self.ammo_sprites:
            sp.delete()
