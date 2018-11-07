from  pyglet.window import key

from .base import Entity
from .weapon import Weapon

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

