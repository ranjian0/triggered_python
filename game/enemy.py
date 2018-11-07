import math
import enum
import pyglet as pg
import itertools as it

from .weapon    import Bullet
from .signal    import connect
# from .level     import get_current_level
from .physics   import RAYCAST_FILTER, COLLISION_MAP
from .core      import angle, distance_sqr, normalize

class EnemyState(enum.Enum):
    IDLE    = 0
    PATROL  = 1
    CHASE   = 2
    ATTACK  = 3

class Enemy:
    COL_TYPES = []

    def __init__(self, position, size, image, waypoints, col_type, physics):
        self.batch = pg.graphics.Batch()
        self.physics = physics
        # -- movement properties
        self.pos   = position
        self.size  = size
        self.speed = 100
        self.angle = 0
        # --health properties
        self.health = 100
        self.damage = 10
        self.dead = False
        # -- weapon properties
        self.bullets = []
        self.muzzle_offset = (self.size[0]/2+Bullet.SIZE/2, -self.size[1]*.21)
        self.muzzle_mag = math.sqrt(distance_sqr((0, 0), self.muzzle_offset))
        self.muzzle_angle = angle(self.muzzle_offset)

        # -- patrol properties
        self.state = EnemyState.IDLE

        self.waypoints = it.cycle(waypoints)
        self.patrol_target = next(self.waypoints)
        self.return_path = None
        self.return_target = None
        self.epsilon = 10
        self.chase_radius = 300
        self.attack_radius = 150
        self.attack_frequency = 10
        self.current_attack = 0

        # Create enemy Image
        self.image = image
        self.image.width = size[0]
        self.image.height = size[1]
        self.image.anchor_x = size[0]/2
        self.image.anchor_y = size[1]/2
        self.sprite = pg.sprite.Sprite(self.image, x=position[0], y=position[1],
            batch=self.batch)

        # enemy physics
        self.body = pm.Body(1, 100)
        self.body.position = self.pos
        self.shape = pm.Circle(self.body, size[0]*.45)
        self.shape.collision_type = col_type
        self.shape.filter = pm.ShapeFilter(categories=RAYCAST_FILTER)
        physics.add(self.body, self.shape)

        self.map = None
        self.player_position = (0, 0)

        # collision handlers
        physics.add_collision_handler(
                col_type,
                COLLISION_MAP.get("PlayerBulletType"),
                handler_begin = self.collide_player_bullet
            )

        connect("on_player_move", self, "_player_moved")

    def _player_moved(self, pos):
        self.player_position = pos

    def collide_player_bullet(self, arbiter, space, data):
        bullet = arbiter.shapes[1]
        bullet.cls_object.destroy()

        space.remove(bullet.body, bullet)
        self.do_damage()
        return False

    def do_damage(self):
        self.health -= self.damage
        if self.health < 0: return
        if self.health == 0:
            self.physics.remove(self.body, self.shape)
            self.bullets.clear()

            self.sprite.batch = None
            self.dead = True

    def set_map(self, _map):
        self.map = _map

    def offset(self):
        px, py = self.pos
        w, h = window.get_size()
        return -px + w/2, -py + h/2

    def look_at(self, target):
        tx, ty = target
        px, py = self.pos
        self.angle = math.degrees(-math.atan2(ty - py, tx - px))
        self.sprite.update(rotation=self.angle)

    def draw(self):
        self.batch.draw()

    def update(self, dt):
        player = get_current_level().get_player()

        if not player:
            player_distance = distance_sqr(self.player_position, self.pos)
            previous_state = self.state

            if player_distance < self.chase_radius**2:
                hit = self.physics.raycast(self.pos, self.player_position, 1, RAYCAST_MASK)
                if hit:
                    self.state = EnemyState.PATROL
                else:
                    self.state = EnemyState.CHASE
            else:
                #self.state = EnemyState.PATROL
                if previous_state == EnemyState.CHASE:
                    hit = self.physics.raycast(self.pos, self.player_position, 1, RAYCAST_MASK)
                    if hit:
                        self.state = EnemyState.PATROL
                        # -- renavigate to current patrol target if its not in our line of sight
                        if self.physics.raycast(self.pos, self.patrol_target, 1, RAYCAST_MASK):
                            pathfinder = self.map.pathfinder
                            pos = pathfinder.closest_point(self.pos)
                            target = pathfinder.closest_point(self.patrol_target)

                            self.return_path = iter(pathfinder.calculate_path(pos, target))
                            self.return_target = next(self.return_path)

                    else:
                        # if player in line of sight, keep chasing
                        self.state = EnemyState.CHASE
        else:
            self.state = EnemyState.PATROL

        if self.state == EnemyState.IDLE:
            self.state = EnemyState.PATROL
        elif self.state == EnemyState.PATROL:
            if self.return_path:
                self.return_path = self.return_to_patrol(dt, self.return_path)
            else:
                self.patrol(dt)
        elif self.state == EnemyState.CHASE:
            self.chase(self.player_position, dt)

        # -- update bullets
        self.bullets = [b for b in self.bullets if not b.destroyed]
        for bullet in self.bullets:
            bullet.update(dt)

    def chase(self, target, dt):
        self.look_at(target)
        if distance_sqr(self.pos, target) > self.attack_radius**2:
            self.move_to_target(target, dt)
        self.attack(target)

    def patrol(self, dt):
        distance = distance_sqr(self.pos, self.patrol_target)
        if distance < self.epsilon:
            self.patrol_target = next(self.waypoints)

        self.look_at(self.patrol_target)
        self.move_to_target(self.patrol_target, dt)

    def return_to_patrol(self, dt, path):
        # -- get enemy back to waypoints after chasing player
        distance = distance_sqr(self.pos, self.return_target)
        if distance < self.epsilon:
            try:
                self.return_target = next(path)
            except StopIteration:
                return None

        self.look_at(self.return_target)
        self.move_to_target(self.return_target, dt)
        return path

    def attack(self, target):
        self.current_attack += 1

        if self.current_attack == self.attack_frequency:
            px, py = self.pos
            diff = target[0] - px, target[1] - py
            _dir = normalize(diff)

            angle = self.muzzle_angle - self.angle
            dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            px += dx * self.muzzle_mag
            py += dy * self.muzzle_mag

            b = Bullet((px, py), _dir, self.batch, collision_type=COLLISION_MAP.get("EnemyBulletType"), physics=self.physics)
            self.bullets.append(b)

            self.current_attack = 0

    def move_to_target(self, target, dt):
        diff = target[0] - self.pos[0], target[1] - self.pos[1]
        if distance_sqr((0, 0), diff):
            dx, dy = normalize(diff)

            bx, by = self.body.position
            bx += dx * self.speed * dt
            by += dy * self.speed * dt
            self.body.position = (bx, by)

            self.sprite.position = (bx, by)
            self.pos = (bx, by)

