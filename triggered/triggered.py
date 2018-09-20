import os
import sys
import math
import heapq
import random
import pprint as pp
import pyglet as pg
import pymunk as pm
import itertools as it

from enum import Enum
from pyglet.gl import *
from pyglet.window import key, mouse
from contextlib import contextmanager
from pymunk import pyglet_util as putils
from collections import defaultdict, namedtuple

FPS        = 60
DEBUG      = 0
SIZE       = (800, 600)
CAPTION    = "Triggered"
BACKGROUND = (100, 100, 100)

KEYS = key.KeyStateHandler()
KEYMAP = {
    key.W : (0, 1),
    key.S : (0, -1),
    key.A : (-1, 0),
    key.D : (1, 0)
}
PAUSE_KEY = key.P

RAYCAST_FILTER = 0x1
RAYCAST_MASK = pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS ^ RAYCAST_FILTER)
COLLISION_MAP = {
    "PlayerType" : 1,
    "EnemyType"  : 2,
    "WallType"   : 3,
    "PlayerBulletType" : 4,
    "EnemyBulletType"  : 5
}


class EventType(Enum):
    KEY_DOWN = 1
    KEY_UP   = 2
    MOUSE_DOWN = 3
    MOUSE_UP   = 4
    MOUSE_MOTION = 5
    RESIZE = 6

Resource = namedtuple("Resource", "name data")

'''
============================================================
---   CLASSES
============================================================
'''
class GameState(Enum):
    MAINMENU    = 1
    RUNNING     = 2
    PAUSED      = 3

class Game:

    def __init__(self):
        self.state = GameState.MAINMENU

        self.mainmenu = MainMenu()
        self.pausemenu = PauseMenu()

        self.manager = LevelManager()
        self.manager.add([
                Level("Kill them all", Resources.instance.level("test"))
            ])

    def draw(self):
        if self.state == GameState.MAINMENU:
            self.mainmenu.draw()
        elif self.state == GameState.PAUSED:
            self.pausemenu.draw()
        elif self.state == GameState.RUNNING:
            self.manager.draw()

    def event(self, *args, **kwargs):
        if self.state == GameState.MAINMENU:
            _type = args[0]
            if _type == EventType.KEY_DOWN:
                if args[1] == key.SPACE:
                    self.state = GameState.RUNNING

        elif self.state == GameState.PAUSED:
            _type = args[0]
            if _type == EventType.KEY_DOWN:
                if args[1] == PAUSE_KEY:
                    self.state = GameState.RUNNING

        elif self.state == GameState.RUNNING:
            self.manager.event(*args, **kwargs)

            _type = args[0]
            if _type == EventType.KEY_DOWN:
                if args[1] == PAUSE_KEY:
                    self.state = GameState.PAUSED

    def update(self, dt):
        if self.state == GameState.MAINMENU:
            self.mainmenu.update(dt)
        elif self.state == GameState.RUNNING:
            self.manager.update(dt)
        elif self.state == GameState.PAUSED:
            self.pausemenu.update(dt)


class Resources:

    # -- singleton
    instance = None
    def __new__(cls):
        if Resources.instance is None:
            Resources.instance = object.__new__(cls)
        return Resources.instance

    def __init__(self, root_dir="res"):
        self.root = root_dir
        pg.resource.path = [
            os.path.join(os.path.dirname(os.path.realpath(__file__)), self.root)
        ]
        pg.resource.reindex()

        abspath = os.path.abspath
        self._sprites = abspath(os.path.join(root_dir, "sprites"))
        self._sounds  = abspath(os.path.join(root_dir, "sounds"))
        self._levels  = abspath(os.path.join(root_dir, "levels"))

        self._data = defaultdict(list)
        self._load()

    def sprite(self, name):
        for res in self._data['sprites']:
            if res.name == name:
                return res.data
        return None

    def sound(self, name):
        for res in self._data['sounds']:
            if res.name == name:
                return res.data
        return None

    def level(self, name):
        for res in self._data['levels']:
            if res.name == name:
                return self._parse_level(res.data)
        return None

    def _load(self):

        # -- load sprites
        for sprite in os.listdir(self._sprites):
            img = pg.resource.image('sprites/' + sprite)
            fn = os.path.basename(sprite.split('.')[0])
            self._data['sprites'].append(Resource(fn,img))

        # -- load sounds
        for sound in os.listdir(self._sounds):
            snd = pg.resource.media('sounds/' + sound)
            fn = os.path.basename(sound.split('.')[0])
            self._data['sounds'].append(Resource(fn,snd))

        # -- load levels
        for level in os.listdir(self._levels):
            lvl = pg.resource.file('levels/' + level, 'r')
            fn = os.path.basename(level.split('.')[0])
            self._data['levels'].append(Resource(fn,lvl))

    def _parse_level(self, file):
        result = []
        for line in file.readlines():
            result.append(list(line.strip()))
        return result

class Physics:

    # -- singleton
    instance = None
    def __new__(cls):
        if Physics.instance is None:
            Physics.instance = object.__new__(cls)
        return Physics.instance


    def __init__(self, steps=50):
        self.space = pm.Space()
        self.steps = steps

        setup_collisions(self.space)

    def add(self, *args):
        self.space.add(*args)

    def remove(self, *args):
        self.space.remove(*args)

    def update(self):
        for _ in it.repeat(None, self.steps):
            self.space.step(0.1 / self.steps)

    def raycast(self, start, end, radius, filter):
        res = self.space.segment_query_first(start, end, radius, filter)
        return res

    def add_collision_handler(self, type_a, type_b,
        handler_begin=None, handler_pre=None, handler_post=None,
        handler_separate=None, data=None):

        handler = self.space.add_collision_handler(type_a, type_b)
        if data:
            handler.data.update(data)

        if handler_begin:
            handler.begin = handler_begin
        if handler_pre:
            handler.pre_solve = handler_pre
        if handler_post:
            handler.post_solve = handler_post
        if handler_separate:
            handler.separate = handler_separate

    def debug_draw(self):
        options = putils.DrawOptions()
        self.space.debug_draw(options)


class Player:

    def __init__(self, position, size, image, batch, _map):
        # --
        self.batch = batch
        self.map = _map

        # -- movement properties
        self.pos    = position
        self.size   = size
        self.angle  = 0
        self.speed  = 100
        # -- health properties
        self.dead = False
        self.health = 100
        self.damage = 5
        self.healthbar = HealthBar((10, window.height))
        # -- weapon properties
        self.ammo   = 150
        self.bullets = []

        # Create Player Image
        self.image = image
        self.image.width = size[0]
        self.image.height = size[1]
        self.image.anchor_x = size[0]/2
        self.image.anchor_y = size[1]/2
        self.sprite = pg.sprite.Sprite(self.image, x=position[0], y=position[1],
            batch=self.batch)

        # player physics
        self.body = pm.Body(1, 100)
        self.body.position = self.pos
        self.shape = pm.Circle(self.body, size[0]*.45)
        self.shape.collision_type = COLLISION_MAP.get("PlayerType")
        self.shape.filter = pm.ShapeFilter(categories=RAYCAST_FILTER)
        Physics.instance.add(self.body, self.shape)

        # -- weird bug - have to push twice
        window.push_handlers(KEYS)
        window.push_handlers(KEYS)

        # -- collision handlers
        Physics.instance.add_collision_handler(
                COLLISION_MAP.get("PlayerType"),
                COLLISION_MAP.get("EnemyBulletType"),
                handler_begin = self.bullet_hit
            )

    def bullet_hit(self, arbiter, space, data):
        bullet = arbiter.shapes[1]
        Physics.instance.remove(bullet.body, bullet)
        self.do_damage()
        return False

    def do_damage(self):
        self.health -= self.damage
        if self.health > 0:
            self.healthbar.set_value(self.health / 100)
        if self.health <= 0:
            Physics.instance.remove(self.body, self.shape)
            self.bullets.clear()
            self.sprite.batch = None
            self.dead = True

    def offset(self):
        # -- calculate distance of player from window center
        # -- usefull for screen scrolling to keep player at center of view
        px, py = self.pos
        w, h = window.get_size()
        return -px + w/2, -py + h/2

    def screen_coords(self):
        # -- convert player coordinates into screen coordinates
        ox, oy = self.map.clamped_offset(*self.offset())
        px, py = self.pos

        cx, cy = px + ox, py + oy
        return cx, cy

    def shoot(self, _dir):
        # -- reduce ammo
        if self.ammo <= 0: return
        self.ammo -= 1

        # -- eject bullet
        px, py = self.pos
        _dir = normalize(_dir)

        px += _dir[0] * self.size[0]*.75
        py += _dir[1] * self.size[1]*.75

        b = Bullet((px, py), _dir, self.batch)
        b.set_col_type(COLLISION_MAP.get("PlayerBulletType"))
        self.bullets.append(b)

    def event(self, type, *args, **kwargs):
        if type == EventType.MOUSE_MOTION:
            x, y, dx, dy = args
            px, py = self.screen_coords()
            self.angle = math.degrees(-math.atan2(y - py, x - px))

        elif type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args

            if btn == mouse.LEFT:
                px, py = self.screen_coords()
                direction = x - px, y - py
                self.shoot(direction)

    def update(self, dt):
        self.sprite.update(rotation=self.angle)

        # -- movements
        dx, dy = 0, 0
        for _key, _dir in KEYMAP.items():
            if KEYS[_key]:
                dx, dy = _dir

        # -- running
        speed = self.speed
        if KEYS[key.RSHIFT] or KEYS[key.LSHIFT]:
            speed *= 2.5

        bx, by = self.body.position
        bx += dx * dt * speed
        by += dy * dt * speed
        self.body.position = (bx, by)

        self.sprite.position = (bx, by)
        self.pos = (bx, by)

        # -- update bullets
        self.bullets = [b for b in self.bullets if not b.destroyed]
        for bullet in self.bullets:
            bullet.update(dt)

        # -- update health bar
        self.healthbar.set_pos((10, window.height))

class EnemyState(Enum):
    IDLE    = 0
    PATROL  = 1
    CHASE   = 2
    ATTACK  = 3

class Enemy:

    def __init__(self, position, size, image, waypoints, batch):
        # -- movement properties
        self.pos   = position
        self.size  = size
        self.speed = 100
        # --health properties
        self.health = 100
        self.damage = 10
        self.dead = False
        # -- weapon properties
        self.bullets = []
        # --
        self.batch = batch

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
        self.shape.collision_type = COLLISION_MAP.get("EnemyType")
        self.shape.filter = pm.ShapeFilter(categories=RAYCAST_FILTER)
        Physics.instance.add(self.body, self.shape)

        self.map = None
        self.player_target = None

        # collision handlers
        Physics.instance.add_collision_handler(
                COLLISION_MAP.get("EnemyType"),
                COLLISION_MAP.get("PlayerBulletType"),
                handler_begin = self.bullet_hit
            )

    def bullet_hit(self, arbiter, space, data):
        bullet = arbiter.shapes[1]
        Physics.instance.remove(bullet.body, bullet)
        self.do_damage()
        return False

    def do_damage(self):
        self.health -= self.damage
        if self.health <= 0:
            Physics.instance.remove(self.body, self.shape)
            self.bullets.clear()
            self.sprite.batch = None
            self.dead = True

    def watch(self, player):
        self.player_target = player

    def set_map(self, _map):
        self.map = _map

    def offset(self):
        px, py = self.pos
        w, h = window.get_size()
        return -px + w/2, -py + h/2

    def look_at(self, target):
        tx, ty = target
        px, py = self.pos
        angle = math.degrees(-math.atan2(ty - py, tx - px))
        self.sprite.update(rotation=angle)

    def update(self, dt):
        player = self.player_target

        if not player.dead:
            player_distance = distance_sqr(player.pos, self.pos)
            previous_state = self.state

            if player_distance < self.chase_radius**2:
                hit = Physics.instance.raycast(self.pos, player.pos, 1, RAYCAST_MASK)
                if hit:
                    self.state = EnemyState.PATROL
                else:
                    self.state = EnemyState.CHASE
            else:
                #self.state = EnemyState.PATROL
                if previous_state == EnemyState.CHASE:
                    hit = Physics.instance.raycast(self.pos, player.pos, 1, RAYCAST_MASK)
                    if hit:
                        self.state = EnemyState.PATROL
                        # -- renavigate to current patrol target if its not in our line of sight
                        if Physics.instance.raycast(self.pos, self.patrol_target, 1, RAYCAST_MASK):
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
            self.chase(player.pos, dt)

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

            px += _dir[0] * self.size[0]
            py += _dir[1] * self.size[1]

            b = Bullet((px, py), _dir, self.batch)
            b.set_col_type(COLLISION_MAP.get("EnemyBulletType"))
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

class Bullet:

    def __init__(self, position, direction, batch, speed=500):
        self.pos = position
        self.dir = direction
        self.speed = speed
        self.batch = batch
        self.destroyed = False

        # image
        sz = 12
        self.image = Resources.instance.sprite("bullet")
        self.image.width = sz
        self.image.height = sz
        self.image.anchor_x = sz/2
        self.image.anchor_y = sz/2
        self.sprite = pg.sprite.Sprite(self.image, x=position[0], y=position[1],
            batch=self.batch)

        angle = math.degrees(-math.atan2(direction[1], direction[0]))
        self.sprite.update(rotation=angle)

        # Bullet physics
        self.body = pm.Body(1, 100)
        self.body.position = self.pos
        self.shape = pm.Circle(self.body, 10) #pm.Poly.create_box(self.body, size=(sz, sz)) -- no rotation
        self.shape.filter = pm.ShapeFilter(categories=RAYCAST_FILTER)
        Physics.instance.add(self.body, self.shape)

    def set_col_type(self, _type):
        self.shape.collision_type = _type

    def update(self, dt):
        bx, by = self.body.position
        dx, dy = self.dir

        bx += dx * dt * self.speed
        by += dy * dt * self.speed

        self.body.position = (bx, by)
        self.sprite.position = (bx, by)
        self.pos = (bx, by)

        if not self.body in Physics.instance.space.bodies:
            self.destroyed = True

class Map:

    def __init__(self, data,
                    wall_img  = None,
                    node_size = 200,
                    physics   = None):

        self.data       = data
        self.node_size  = node_size
        self.wall_img   = Resources.instance.sprite("wall_image")
        self.wall_img.width = node_size//2
        self.wall_img.height = node_size//2

        self.floor_img   = Resources.instance.sprite("floor")
        self.floor_img.width = node_size//2
        self.floor_img.height = node_size//2

        self.sprites    = []
        self.batch      = pg.graphics.Batch()
        self.make_map()

        self.pathfinder = PathFinder(data, node_size)
        self.spawn_data = self.parse_spawn_points()

    def make_map(self):
        nsx, nsy = (self.node_size,)*2
        sx = (len(self.data[0]) * nsx) - nsx/2
        sy = (len(self.data) * nsy) - nsy/2

        # physics options
        wsx, wsy = (nsx//2, nsy//2)

        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                offx, offy = x * nsx, y * nsy

                # -- create floor tiles
                sp = pg.sprite.Sprite(self.floor_img, x=offx, y=offy, batch=self.batch)
                self.sprites.append(sp)

                directions = [(1, 0), (0, 1), (1,1)]
                for dx, dy in directions:
                    px = offx + (dx * nsx/2)
                    py = offy + (dy * nsx/2)
                    s = pg.sprite.Sprite(self.floor_img, x=px, y=py, batch=self.batch)

                    if dx:
                        s.anchor_x = self.floor_img.width/2
                        s.anchor_y = self.floor_img.height/2
                        s.update(rotation=90)
                    self.sprites.append(s)

                # -- create walls
                if data == "#":
                    sp = pg.sprite.Sprite(self.wall_img, x=offx, y=offy, batch=self.batch)
                    self.sprites.append(sp)
                    add_wall((offx + wsx/2, offy + wsy/2), (wsx, wsy))

                    # Fill gaps
                    # -- gaps along x-axis
                    if x < len(row) - 1 and self.data[y][x + 1] == "#":
                        sp = pg.sprite.Sprite(self.wall_img, x=offx + nsx/2, y=offy, batch=self.batch)
                        self.sprites.append(sp)
                        add_wall((offx + wsx/2 + nsx/2, offy + wsy/2), (wsx, wsy))


                    # -- gaps along y-axis
                    if y < len(self.data) - 1 and self.data[y + 1][x] == "#":
                        sp = pg.sprite.Sprite(self.wall_img, x=offx, y=offy + nsy/2, batch=self.batch)
                        self.sprites.append(sp)
                        add_wall((offx + wsx/2, offy + wsy/2 + nsy/2), (wsx, wsy))

    def parse_spawn_points(self):
        spawn_data = {
            'player_position' : None,   # identifier == 'p'
            'enemy_position'  : [],     # identifier == 'e'
            'mino_position'   : None,   # identifier == 'm'
            'vip_position'    : None,   # identifier == 'v'
            'time_stone'      : None,   # identifier == 't'

            'patrol_positions': [],     # anything but '#', used for enemy patrol
        }

        nsx, nsy = (self.node_size,)*2
        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                location = (x*nsx, y*nsy)

                if   data == "p":
                    spawn_data['player_position'] = location
                elif data == 'e':
                    spawn_data['enemy_position'].append(location)
                elif data == 'm':
                    spawn_data['mino_position'] = location
                elif data == 'v':
                    spawn_data['vip_position'] = location
                elif data == 't':
                    spawn_data['time_stone'] = location

                if data != '#':
                    spawn_data['patrol_positions'].append(location)
        return spawn_data

    def clamp_player(self, player):
        # -- keep player within map bounds
        offx, offy = self.clamped_offset(*player.offset())

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(offx, offy, 0)

    def clamped_offset(self, offx, offy):
        # -- clamp offset so that viewport doesnt go beyond map bounds
        winw, winh = window.get_size()
        msx, msy = self.size()

        clamp_X = msx - winw
        clamp_Y = msy - winh

        offx = 0 if offx > 0 else offx
        offx = -clamp_X if offx < -clamp_X else offx
        offy = 0 if offy > 0 else offy
        offy = -clamp_Y if offy < -clamp_Y else offy

        return offx, offy

    def draw(self):
        self.batch.draw()

    def size(self):
        ns = self.node_size
        return (ns * len(self.data[0]))-ns//2, (ns * len(self.data))-ns//2

    def __getitem__(self, val):
        return self.spawn_data.get(val, None)

class PathFinder:

    def __init__(self, map_data, node_size):
        self.data = map_data
        self.node_size = (node_size,)*2

    def walkable(self):
        # -- find all walkable nodes
        mul = lambda p1, p2 : (p1[0]*p2[0], p1[1]*p2[1])

        walkable = [mul((x, y), self.node_size) for y, data in enumerate(self.data)
            for x, d in enumerate(data) if d != '#']
        return walkable

    def calculate_path(self, p1, p2):
        cf, cost = a_star_search(self, p1, p2)
        return reconstruct_path(cf, p1, p2)

    def calc_patrol_path(self, points):
        result = []
        circular_points = points + [points[0]]
        for i in range(len(circular_points)-2):
            f, s = circular_points[i:i+2]
            path = self.calculate_path(f, s)[1:]
            result.extend(path)
        return result

    def neighbours(self, p):
        add = lambda p1, p2 : (p1[0]+p2[0], p1[1]+p2[1])
        mul = lambda p1, p2 : (p1[0]*p2[0], p1[1]*p2[1])

        # -- find neighbours that are walkable
        directions      = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neigh_positions = [add(p, mul(d, self.node_size)) for d in directions]
        return [n for n in neigh_positions if n in self.walkable()]

    def closest_point(self, p):
        data = [(distance_sqr(p, point), point) for point in self.walkable()]
        return min(data, key=lambda d:d[0])[1]

    def cost(self, *ignored):
        return 1

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class LevelStatus(Enum):
    RUNNING = 1
    FAILED  = 2
    PASSED  = 3

class Level:

    def __init__(self, name, data):
        self.name = name
        self.data = data

        self.map = None
        self.agents = []
        self.agent_batch = pg.graphics.Batch()

        self.hud = HUD()
        self.reload()

        self.status = LevelStatus.RUNNING

    def reload(self):
        self.agents.clear()
        self.map = Map(self.data, physics=Physics.instance)

        # -- add player to map position
        player = Player(self.map['player_position'], (50, 50),
            Resources.instance.sprite("hitman1_gun"), self.agent_batch, self.map)
        self.agents.append(player)
        self.hud.add(player.healthbar)

        # -- add other agents map positions
        for point in self.map['enemy_position']:
            patrol_point = random.choice(self.map['patrol_positions'])

            patrol = self.map.pathfinder.calc_patrol_path([point, patrol_point])
            path = patrol + list(reversed(patrol[1:-1]))
            e = Enemy(point, (50, 50), Resources.instance.sprite("robot1_gun"), path, self.agent_batch)
            if DEBUG:
                e.debug_data = (patrol, random_color())
            e.watch(player)
            e.set_map(self.map)
            self.agents.append(e)

    def get_player(self):
        for ag in self.agents:
            if isinstance(ag, Player):
                return ag
        return None

    def get_enemies(self):
        return [e for e in self.agents if isinstance(e, Enemy)]

    def draw(self):
        self.map.draw()
        self.agent_batch.draw()
        self.hud.draw()

        if DEBUG:
            for agent in self.agents:
                if isinstance(agent, Enemy):
                    path, color = agent.debug_data
                    debug_draw_point(agent.pos, color, 10)
                    debug_draw_path(path, color)

    def update(self, dt):
        if DEBUG:
            if hasattr(self, 'switch_view') and self.switch_view:
                self.map.clamp_player(self.get_enemies()[0])
            else:
                self.map.clamp_player(self.get_player())
        else:
            self.map.clamp_player(self.get_player())

        # -- remove dead enemies
        for agent in self.agents:
            if isinstance(agent, Enemy) and agent.dead:
                self.agents.remove(agent)

        for agent in self.agents:
            agent.update(dt)

        # -- change level status
        if self.get_player().dead:
            self.status = LevelStatus.FAILED

        if len(self.get_enemies()) == 0:
            self.status = LevelStatus.PASSED

    def event(self, *args, **kwargs):
        for agent in self.agents:
            if hasattr(agent, 'event'):
                agent.event(*args, **kwargs)

        if DEBUG:
            _type = args[0]

            if _type == EventType.KEY_DOWN:
                k = args[1]
                if k == key.TAB:
                    if hasattr(self, 'switch_view'):
                        self.switch_view = not self.switch_view
                    else:
                        self.switch_view = True

class LevelManager:

    def __init__(self):
        self.levels = []
        self.index = 0

        self.completed = False

    def add(self, levels):
        if isinstance(levels, list):
            self.levels.extend(levels)
        else:
            self.levels.append(levels)

    def current(self):
        return self.levels[self.index]

    def next(self):
        self.completed = self.index == len(self.levels) - 1
        if not self.completed:
            self.index += 1
            return self.current()
        return None

    def __iter__(self):
        for l in self.levels:
            yield l

    def draw(self):
        self.current().draw()

    def update(self, dt):
        self.current().update(dt)

    def event(self, *args, **kwargs):
        self.current().event(*args, **kwargs)


class HUD:

    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def draw(self):
        with reset_matrix():
            for item in self.items:
                item.draw()

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

class MainMenu:

    def __init__(self):
        self.title = pg.text.Label("TRIGGERED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')

        self.instruction = pg.text.Label("Press Space to play",
            x=window.width/2, y=10, anchor_x='center')

    def draw(self):
        with reset_matrix():
            self.title.draw()
            self.instruction.draw()

    def update(self, dt):
        # -- change location on resize
        hw = window.width/2

        self.title.x = hw
        self.title.y = window.height * .9

        self.instruction.x = hw

class PauseMenu:

    def __init__(self):
        self.title = pg.text.Label("PAUSED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')

    def draw(self):
        with reset_matrix():
            self.title.draw()

    def update(self, dt):
        # -- change location on resize
        hw = window.width/2

        self.title.x = hw
        self.title.y = window.height * .9

'''
============================================================
---   FUNCTIONS
============================================================
'''
def normalize(p):
    mag = math.sqrt(distance_sqr((0, 0), p))
    if mag:
        x = p[0] / mag
        y = p[1] / mag
        return (x, y)
    return p

@contextmanager
def reset_matrix():
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window.width, 0, window.height, -1, 1)

    yield

    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def distance_sqr(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx**2 + dy**2

def add_wall(pos, size):
    space = Physics.instance.space

    shape = pm.Poly.create_box(space.static_body, size=size)
    shape.collision_type = COLLISION_MAP.get("WallType")
    shape.body.position = pos
    space.add(shape)

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def random_color():
    r = random.random()
    g = random.random()
    b = random.random()
    return (r, g, b, 1)

def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbours(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.append(start)
    path.reverse()
    return path

def setup_collisions(space):

    # Player-Enemy Collision
    def player_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        pshape = arbiter.shapes[0]
        eshape  = arbiter.shapes[1]

        normal = pshape.body.position - eshape.body.position
        normal = normal.normalized()
        pshape.body.position = eshape.body.position + (normal * (pshape.radius*2))
        return True

    handler = space.add_collision_handler(
            COLLISION_MAP.get("PlayerType"),
            COLLISION_MAP.get("EnemyType")
        )
    handler.begin = player_enemy_solve

    # Enemy-Enemy Collision
    def enemy_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        eshape  = arbiter.shapes[0]
        eshape1 = arbiter.shapes[1]

        normal = eshape.body.position - eshape1.body.position
        normal = normal.normalized()
        eshape.body.position = eshape1.body.position + (normal * (eshape.radius*2))
        return True

    handler = space.add_collision_handler(
            COLLISION_MAP.get("EnemyType"),
            COLLISION_MAP.get("EnemyType")
        )
    handler.begin = enemy_enemy_solve

    # Bullet Collisions
    def bullet_wall_solve(arbiter, space, data):
        bullet = arbiter.shapes[0]
        Physics.instance.remove(bullet.body, bullet)
        return False

    # -- player bullets
    handler1 = space.add_collision_handler(
            COLLISION_MAP.get("PlayerBulletType"),
            COLLISION_MAP.get("WallType")
        )
    handler1.begin = bullet_wall_solve

    # -- enemy bullets
    handler2 = space.add_collision_handler(
            COLLISION_MAP.get("EnemyBulletType"),
            COLLISION_MAP.get("WallType")
        )
    handler2.begin = bullet_wall_solve

def debug_draw_point(pos, color=(1, 0, 0, 1), size=5):
    glColor4f(*color)
    glPointSize(size)

    glBegin(GL_POINTS)
    glVertex2f(*pos)
    glEnd()

def debug_draw_line(start, end, color=(1, 1, 0, 1), width=2):
    glColor4f(*color)
    glLineWidth(width)

    glBegin(GL_LINES)
    glVertex2f(*start)
    glVertex2f(*end)
    glEnd()

def debug_draw_path(points, color=(1, 0, 1, 1), width=5):
    glColor4f(*color)
    glLineWidth(width)

    glBegin(GL_LINE_STRIP)
    for point in points:
        glVertex2f(*point)
    glEnd()

'''
============================================================
---   MAIN
============================================================
'''

# -- create window
window = pg.window.Window(*SIZE, resizable=True)
window.set_minimum_size(*SIZE)
window.set_caption(CAPTION)

fps  = pg.window.FPSDisplay(window)
res  = Resources()
phy  = Physics()
game = Game()

@window.event
def on_draw():
    window.clear()
    glClearColor(.39, .39, .39, 1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    game.draw()

    if DEBUG:
        fps.draw()
        phy.debug_draw()

@window.event
def on_resize(w, h):
    pass

@window.event
def on_key_press(key, modifiers):
    game.event(EventType.KEY_DOWN, key, modifiers)

@window.event
def on_key_release(key, modifiers):
    game.event(EventType.KEY_UP, key, modifiers)

@window.event
def on_mouse_press(x, y, button, modifiers):
    game.event(EventType.MOUSE_DOWN, x, y, button, modifiers)

@window.event
def on_mouse_release(x, y, button, modifiers):
    game.event(EventType.MOUSE_UP, x, y, button, modifiers)

@window.event
def on_mouse_motion(x, y, dx, dy):
    game.event(EventType.MOUSE_MOTION, x, y, dx, dy)

def on_update(dt):
    phy.update()
    game.update(dt)

if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/FPS)
    pg.app.run()