from  pyglet.window import key

from .base import Entity
from .weapon import Weapon

KEYMAP = {
    key.W : (0, 1),
    key.S : (0, -1),
    key.A : (-1, 0),
    key.D : (1, 0)
}

class Player(Entity, key.KeyStateHandler):

    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
        self.set_speed(100)

        # Player Collision
        self.set_collision_type(COLLISION_MAP.get("PlayerType"))
        self.set_collision_filter(pm.ShapeFilter(categories=RAYCAST_FILTER))
        self.collide_with(COLLISION_MAP.get("EnemyBulletType"))
        self.on_collision_enter.connect(self.on_collision)

        # Player Health
        self.healthbar = HealthBar((10, window.height))
        self.on_damage.connect(self.update_damage)

        # Player Weapon
        self.weapon = Weapon(self.size)
        self.ammobar = AmmoBar((10, window.height - (AmmoBar.AMMO_IMG_HEIGHT*1.5)), self.weapon.ammo)
        self.weapon.on_fire.connect(self.update_weapon)

    def update_damage(self):
        self.healthbar.set_value(self.health / self.max_health)
        if self.dead:
            self.destroy()

    def update_weapon(self, *args):
        self.ammobar.set_value(self.weapon.ammo)

    def screen_position(self):
        # -- player offset
        px, py = self.position
        w, h = window.get_size()
        player_off =  -px + w/2, -py + h/2

        _map = get_current_level().map
        ox, oy = _map.clamped_offset(*player_off)
        px, py = self.position
        return px + ox, py + oy

    def on_collision(self, other, *args):
        arbiter, space, data = args
        if other == COLLISION_MAP.get("EnemyBulletType"):
            # emit damage signal
            self.on_damage()

            # destroy bullet
            bullet = arbiter.shapes[1]
            bullet.cls_object.destroy()
            space.remove(bullet.body, bullet)

        elif other == COLLISION_MAP.get("WallType"):
            pass

    def event(self, _type, *args, **kwargs):
        if _type == EventType.MOUSE_MOTION:
            x, y, dx, dy = args
            px, py = self.screen_position()
            self.rotation = math.degrees(-math.atan2(y - py, x - px))

        elif _type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args
            if btn == mouse.LEFT:
                px, py = self.screen_position()
                direction = normalize((x - px, y - py))
                self.weapon.on_fire(self.position, self.rotation, direction,
                    COLLISION_MAP.get("PlayerBulletType"), self.physics)

        elif type == EventType.RESIZE:
            w, h = args
            self.healthbar.set_pos((10, h))
            self.ammobar.set_pos((10, h - (AmmoBar.AMMO_IMG_HEIGHT*1.5)))

    def draw(self):
        Entity.draw(self)
        self.weapon.draw()

    def update(self, dt):
        Entity.update(self, dt)
        self.weapon.update(dt)
        # -- movement
        dx, dy = 0, 0
        for _key, _dir in KEYMAP.items():
            if self[_key]:
                dx, dy = _dir

        speed = self.speed*2.5 if any([self[key.LSHIFT], self[key.RSHIFT]]) else self.speed
        self.set_velocity((dx*speed, dy*speed))

        # -- signal position change
        emit_signal("on_player_move", self.position)

    def destroy(self):
        Entity.destroy(self)
        del self.healthbar
        del self.ammobar

        level = get_current_level()
        level.remove(self)



class HUD:

    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def draw(self):
        with reset_matrix():
            for item in self.items:
                item.draw()

    def event(self, *args, **kwargs):
        for item in self.items:
            if hasattr(item, 'event'):
                item.event(*args, **kwargs)

class HealthBar:

    def __init__(self, position):
        self.pos = position
        self.batch = pg.graphics.Batch()

        border = Resources.instance.sprite("health_bar_border")
        border.anchor_y = border.height
        self.border = pg.sprite.Sprite(border, x=position[0], y=position[1], batch=self.batch)

        self.bar_im = Resources.instance.sprite("health_bar")
        self.bar_im.anchor_y = self.bar_im.height
        self.bar = pg.sprite.Sprite(self.bar_im, x=position[0], y=position[1], batch=self.batch)

    def draw(self):
        self.batch.draw()

    def set_value(self, percent):
        region = self.bar_im.get_region(0, 0,
            int(self.bar_im.width*percent), self.bar_im.height)
        region.anchor_y = self.bar_im.height
        self.bar.image = region

    def set_pos(self, pos):
        self.pos = pos
        self.border.update(x=pos[0], y=pos[1])
        self.bar.update(x=pos[0], y=pos[1])

class AmmoBar:
    AMMO_IMG_HEIGHT = 30

    def __init__(self, position, ammo):
        self.pos = position
        self.batch = pg.graphics.Batch()
        self.ammo = ammo

        self.ammo_img = Resources.instance.sprite("ammo_bullet")
        image_set_size(self.ammo_img, self.AMMO_IMG_HEIGHT//3, self.AMMO_IMG_HEIGHT)
        self.ammo_img.anchor_y = self.ammo_img.height
        self.bullets = [pg.sprite.Sprite(self.ammo_img, batch=self.batch)
            for _ in range(ammo // 100)]

        self.ammo_text = pg.text.Label(f" X {self.ammo}", bold=True,
            font_size=12, color=(200, 200, 0, 255), batch=self.batch,
            anchor_y='top', anchor_x='left')

        self.set_pos(position)

    def draw(self):
        self.batch.draw()

    def set_value(self, val):
        self.ammo = val

        num_bul = self.ammo // 100
        if len(self.bullets) > num_bul:
            self.bullets.pop(len(self.bullets)-1)
            self.set_pos(self.pos)

        self.ammo_text.text = f" X {val}"

    def set_pos(self, pos):
        self.pos = pos

        px, py = pos
        offx = self.ammo_img.width + 2
        for idx, bull in enumerate(self.bullets):
            bull.x = px + (idx * offx)
            bull.y = py

        txt_off = px + (len(self.bullets) * offx)
        self.ammo_text.x = txt_off
        self.ammo_text.y = py

