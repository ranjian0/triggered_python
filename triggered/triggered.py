import os
import sys
import math
import heapq
import random
import pickle
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
    "WallType"   : 3,
    "PlayerBulletType" : 4,
    "EnemyBulletType"  : 5
}
ENEMY_COL_TYPE = 100

BULLET_SIZE = 12
MINIMAP_AGENT_SIZE = 25
AMMO_IMG_HEIGHT = 30

class EventType(Enum):
    KEY_DOWN = 1
    KEY_UP   = 2
    MOUSE_DOWN = 3
    MOUSE_UP   = 4
    MOUSE_MOTION = 5
    MOUSE_DRAG = 6
    MOUSE_SCROLL = 7
    RESIZE = 8

Resource = namedtuple("Resource", "name data")
LevelData = namedtuple("LevelData",
            ["map",
             "player",
             "enemies",
             "waypoints",
             "lights",
             "objectives"])

'''
============================================================
---   CLASSES
============================================================
'''
class GameState(Enum):
    MAINMENU    = 1
    RUNNING     = 2
    PAUSED      = 3

    EDITOR      = 4

class Game:

    def __init__(self):
        self.state = GameState.MAINMENU

        self.mainmenu = MainMenu()
        self.pausemenu = PauseMenu()

        self.manager = LevelManager()
        self.manager.add([
                Level("Kill them all", "level_one"),
                Level("Extraction", "level_two")
            ])

        self.editor = LevelEditor()

    def draw(self):
        if self.state == GameState.MAINMENU:
            self.mainmenu.draw()
        elif self.state == GameState.PAUSED:
            self.pausemenu.draw()
        elif self.state == GameState.RUNNING:
            self.manager.draw()
        elif self.state == GameState.EDITOR:
            self.editor.draw()

    def event(self, *args, **kwargs):
        self.mainmenu.event(*args, **kwargs)
        self.pausemenu.event(*args, **kwargs)

        _type = args[0]

        if self.state == GameState.MAINMENU:
            if _type == EventType.KEY_DOWN:
                if args[1] == key.SPACE:
                    self.state = GameState.RUNNING

        elif self.state == GameState.PAUSED:
            if _type == EventType.KEY_DOWN:
                if args[1] == PAUSE_KEY:
                    self.state = GameState.RUNNING

        elif self.state == GameState.RUNNING:
            self.manager.event(*args, **kwargs)

            if _type == EventType.KEY_DOWN:
                if args[1] == PAUSE_KEY:
                    self.state = GameState.PAUSED

            # -- switch to editor
                if args[1] == key.E:
                    self.editor.set(self.manager.current())
                    self.state = GameState.EDITOR

        elif self.state == GameState.EDITOR:
            self.editor.event(*args, **kwargs)

            if _type == EventType.KEY_DOWN:
                # -- switch to game, save edited level
                if args[1] == key.E:
                    self.editor.save()
                    self.state = GameState.RUNNING

        # -- special case Resize event
        if _type == EventType.RESIZE:
            self.editor.event(*args, *kwargs)


    def update(self, dt):
        if self.state == GameState.MAINMENU:
            self.mainmenu.update(dt)
        elif self.state == GameState.RUNNING:
            self.manager.update(dt)
        elif self.state == GameState.PAUSED:
            self.pausemenu.update(dt)
        elif self.state == GameState.EDITOR:
            self.editor.update(dt)


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

    def get_path(self, name):
        # -- determine the full path of a resource called name
        for sprite in os.listdir(self._sprites):
            n = sprite.split('.')[0]
            if n == name:
                return os.path.join(self._sprites, sprite)

        for sound in os.listdir(self._sounds):
            n = sound.split('.')[0]
            if n == name:
                return os.path.join(self._sounds, sound)

        for level in os.listdir(self._levels):
            n = level.split('.')[0]
            if n == name:
                return os.path.join(self._levels, level)
        return None

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
        else:
            # -- filename does not exit, create level file
            fn = name + '.level'
            path = os.path.join(self._levels, fn)
            with open(path, 'w') as _:
                pass

            # -- create level resource
            pg.resource.reindex()
            lvl = pg.resource.file('levels/' + fn, 'r')

            # -- add resource to database
            self._data['levels'].append(Resource(name,lvl))
            print(f"Created new level {name}")
            return self._parse_level(lvl)

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
            lvl = pg.resource.file('levels/' + level)
            fn = os.path.basename(level.split('.')[0])
            self._data['levels'].append(Resource(fn,lvl))

    def _parse_level(self, file):
        try:
            return pickle.load(file)
        except EOFError:
            return None

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
        self.max_health = 900
        self.health = 900
        self.damage = 5
        self.healthbar = HealthBar((10, window.height))
        # -- weapon properties
        self.ammo   = 350
        self.bullets = []
        self.muzzle_offset = (self.size[0]/2+BULLET_SIZE/2, -self.size[1]*.21)
        self.muzzle_mag = math.sqrt(distance_sqr((0, 0), self.muzzle_offset))
        self.muzzle_angle = angle(self.muzzle_offset)
        self.ammobar = AmmoBar((10, window.height - (AMMO_IMG_HEIGHT*1.5)), self.ammo)

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
        if self.health < 0: return
        if self.health > 0:
            self.healthbar.set_value(self.health / self.max_health)
        if self.health == 0:
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
        self.ammobar.set_value(self.ammo)

        # -- eject bullet
        px, py = self.pos
        angle = self.muzzle_angle - self.angle
        dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        px += dx * self.muzzle_mag
        py += dy * self.muzzle_mag

        b = Bullet((px, py), _dir, self.batch)
        b.set_col_type(COLLISION_MAP.get("PlayerBulletType"))
        self.bullets.append(b)

    def event(self, type, *args, **kwargs):
        if type == EventType.MOUSE_MOTION:
            x, y, dx, dy = args
            px, py = self.screen_coords()
            self.angle = math.degrees(-math.atan2(y - py, x - px))
            self.sprite.update(rotation=self.angle)

        elif type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args

            if btn == mouse.LEFT:
                px, py = self.screen_coords()
                direction = normalize((x - px, y - py))
                self.shoot(direction)

        elif type == EventType.RESIZE:
            w, h = args
            self.healthbar.set_pos((10, h))
            self.ammobar.set_pos((10, window.height - (AMMO_IMG_HEIGHT*1.5)))

    def update(self, dt):
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

class EnemyState(Enum):
    IDLE    = 0
    PATROL  = 1
    CHASE   = 2
    ATTACK  = 3

class Enemy:

    def __init__(self, position, size, image, waypoints, batch, col_type):
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
        self.muzzle_offset = (self.size[0]/2+BULLET_SIZE/2, -self.size[1]*.21)
        self.muzzle_mag = math.sqrt(distance_sqr((0, 0), self.muzzle_offset))
        self.muzzle_angle = angle(self.muzzle_offset)
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
        self.shape.collision_type = col_type
        self.shape.filter = pm.ShapeFilter(categories=RAYCAST_FILTER)
        Physics.instance.add(self.body, self.shape)

        self.map = None
        self.player_target = None

        # collision handlers
        Physics.instance.add_collision_handler(
                col_type,
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
        if self.health < 0: return
        if self.health == 0:
            Physics.instance.remove(self.body, self.shape)
            for bul in self.bullets:
                bul.destroy()
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
        self.angle = math.degrees(-math.atan2(ty - py, tx - px))
        self.sprite.update(rotation=self.angle)

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

            angle = self.muzzle_angle - self.angle
            dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            px += dx * self.muzzle_mag
            py += dy * self.muzzle_mag

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
        sz = BULLET_SIZE
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

    def destroy(self):
        self.sprite.batch = None
        Physics.instance.remove(self.body, self.shape)

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
                    node_size = 100,
                    physics   = None):

        self.data       = data
        self.node_size  = node_size
        self.wall_img   = Resources.instance.sprite("wall")
        image_set_size(self.wall_img, node_size, node_size)

        self.floor_img   = Resources.instance.sprite("floor")
        image_set_size(self.floor_img, node_size, node_size)

        self.sprites    = []
        self.batch      = pg.graphics.Batch()
        self.make_map()

        self.pathfinder = PathFinder(self.data, node_size)

    def make_map(self):
        bg = pg.graphics.OrderedGroup(0)
        fg = pg.graphics.OrderedGroup(1)
        nsx, nsy = (self.node_size,)*2

        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                offx, offy = x * nsx, y * nsy

                # -- create floor tiles
                if data == " ":
                    sp = pg.sprite.Sprite(self.floor_img, x=offx, y=offy, batch=self.batch, group=bg)
                    self.sprites.append(sp)

                # -- create walls
                if data == "#":
                    sp = pg.sprite.Sprite(self.wall_img, x=offx, y=offy, batch=self.batch, group=fg)
                    self.sprites.append(sp)
                    add_wall((offx + nsx/2, offy + nsy/2), (nsx, nsy))

    def clamp_player(self, player):
        # -- keep player within map bounds
        offx, offy = self.clamped_offset(*player.offset())

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(offx, offy, 0)

    def clamped_offset(self, offx, offy):
        # -- clamp offset so that viewport doesnt go beyond map bounds
        # -- if map is smaller than window, no need for offset
        winw, winh = window.get_size()
        msx, msy = self.size()

        clamp_X = msx - winw
        clamp_Y = msy - winh

        offx = 0 if offx > 0 else offx
        if clamp_X > 0:
            offx = -clamp_X if offx < -clamp_X else offx

        offy = 0 if offy > 0 else offy
        if clamp_Y > 0:
            offy = -clamp_Y if offy < -clamp_Y else offy

        return offx, offy

    def make_minimap(self, size, wall_color=(255, 255, 0, 200),
        background_color=(0, 0, 0, 0)):
        sx, sy = [s/ms for s, ms in zip(size, self.size())]
        nsx, nsy = (self.node_size,)*2

        background_image = pg.image.SolidColorImagePattern(background_color)
        background_image = background_image.create_image(*self.size())
        background = background_image.get_texture()

        wall_image = pg.image.SolidColorImagePattern(wall_color)
        wall_image = wall_image.create_image(nsx, nsy)
        wall = wall_image.get_texture()

        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                offx, offy = x * nsx, y * nsy

                if data == "#":
                    background.blit_into(wall_image, offx, offy, 0)

        sp = pg.sprite.Sprite(background)
        sp.scale_x = sx
        sp.scale_y = sy
        return sp

    def draw(self):
        self.batch.draw()

    def size(self):
        ns = self.node_size
        return (ns * len(self.data[0])), (ns * len(self.data))

class PathFinder:

    def __init__(self, map_data, node_size):
        self.data = map_data
        self.node_size = (node_size,)*2

    def walkable(self):
        # -- find all walkable nodes
        add = lambda p1, p2 : (p1[0]+p2[0], p1[1]+p2[1])
        mul = lambda p1, p2 : (p1[0]*p2[0], p1[1]*p2[1])

        hns = (self.node_size[0]/2, self.node_size[1]/2)
        walkable = [add(hns, mul((x, y), self.node_size)) for y, data in enumerate(self.data)
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

    def __init__(self, name, resource_name):
        self.name = name
        self.file = Resources.instance.get_path(resource_name)
        self.data = Resources.instance.level(resource_name)

        self.map = None
        self.agents = []
        self.agent_batch = pg.graphics.Batch()

        self.reload()
        self.status = LevelStatus.RUNNING

    def save(self):
        if self.data:
            f = open(self.file, 'wb')
            pickle.dump(self.data, f)

    def reload(self):
        if not self.data: return

        self.hud = HUD()
        self.agents.clear()
        self.map = Map(self.data.map, physics=Physics.instance)

        # -- add player to map position
        player = Player(self.data.player, (50, 50),
            Resources.instance.sprite("hitman1_gun"), self.agent_batch, self.map)
        self.agents.append(player)
        self.hud.add(player.healthbar)
        self.hud.add(player.ammobar)

        # -- add other agents map positions
        for idx, point in enumerate(self.data.enemies):
            # -- get waypoints
            path = self.data.waypoints[idx]

            e = Enemy(point, (50, 50), Resources.instance.sprite("robot1_gun"),
                path, self.agent_batch, ENEMY_COL_TYPE + idx)
            ENEMY_TYPES.append(ENEMY_COL_TYPE + idx)

            if DEBUG:
                e.debug_data = (patrol, random_color())
            e.watch(player)
            e.set_map(self.map)
            self.agents.append(e)

        # -- register collision types
        setup_collisions(Physics.instance.space)

        # -- create infopanel
        self.infopanel = InfoPanel(self.name, self.data.objectives, self.map, self.agents)
        self.show_info = False

    def get_player(self):
        for ag in self.agents:
            if isinstance(ag, Player):
                return ag
        return None

    def get_enemies(self):
        return [e for e in self.agents if isinstance(e, Enemy)]

    def draw(self):
        if not self.data: return

        self.map.draw()
        self.agent_batch.draw()
        self.hud.draw()

        if self.show_info:
            self.infopanel.draw()

        if DEBUG:
            for agent in self.agents:
                if isinstance(agent, Enemy):
                    path, color = agent.debug_data
                    debug_draw_point(agent.pos, color, 10)
                    debug_draw_path(path, color)

    def update(self, dt):
        if not self.data: return

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

        # show info panel
        self.show_info = KEYS[key.TAB]
        if self.show_info:
            self.infopanel.update(dt)

    def event(self, _type, *args, **kwargs):
        if not self.data: return

        self.infopanel.event(_type, *args, **kwargs)
        for agent in self.agents:
            if hasattr(agent, 'event'):
                agent.event(_type, *args, **kwargs)

        if DEBUG:
            if _type == EventType.KEY_DOWN:
                k = args[1]
                if k == key.BACKSPACE:
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

class LevelEditor:

    def __init__(self):
        self._level = None
        self.data = dict()

        self.toolbar = EditorToolbar(self.data)
        self.viewport = EditorViewport(self.data)
        self.properties = EditorToolprops()


    def set(self, level):
        self._level = level
        if level.data:
            # -- load leveldata
            for key, val in level.data._asdict().items():
                self.data[key] = val
        else:
            # -- initialize data with default values
            keys = LevelData._fields
            defaults = ([[]], (-10000, -10000), [], [], [], [])
            for k,v in zip(keys, defaults):
                self.data[k] = v

    def save(self):
        # -- remove temp data from self.data
        tmp_items = [key for key,v in self.data.items() if key.startswith('_')]
        tmp_data = [v for key,v in self.data.items() if key.startswith('_')]
        for it in tmp_items:
            del self.data[it]

        # -- update level data and reload level
        self._level.data = LevelData(**self.data)
        self._level.save()
        self._level.reload()

        # -- restore temp data from self.data
        for key,val in zip(tmp_items, tmp_data):
            self.data[key] = val

        # --  update viewport
        self.viewport.reload()

    def draw(self):
        with reset_matrix():
            self.viewport.draw()
            self.toolbar.draw()

    def update(self, dt):
        self.toolbar.update(dt)
        self.viewport.update(dt)

    def event(self, *args, **kwargs):
        self.toolbar.event(*args, **kwargs)
        self.viewport.event(*args, **kwargs)


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

    def __init__(self, position, ammo):
        self.pos = position
        self.batch = pg.graphics.Batch()
        self.ammo = ammo

        self.ammo_img = Resources.instance.sprite("ammo_bullet")
        self.ammo_img.width = AMMO_IMG_HEIGHT//3
        self.ammo_img.height = AMMO_IMG_HEIGHT
        self.ammo_img.anchor_y = self.ammo_img.height
        self.bullets = [pg.sprite.Sprite(self.ammo_img, batch=self.batch)
            for _ in range(ammo // 100)]

        self.ammo_text = pg.text.Label(f" X {self.ammo}", bold=True,
            font_size=12, color=(200, 200, 0, 255), batch=self.batch,
            anchor_y='top', anchor_x='left')

    def draw(self):
        self.batch.draw()

    def set_value(self, val):
        self.ammo = val

        num_bul = self.ammo // 100
        if len(self.bullets) > num_bul:
            self.bullets.pop(len(self.bullets)-1)

            # -- update position
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

    def event(self, _type, *args, **kwargs):
        if _type == EventType.RESIZE:
            w, h = args

            self.title.x = w/2
            self.title.y = h * .9
            self.instruction.x = w/2


    def update(self, dt):
        pass

class PauseMenu:

    def __init__(self):
        self.title = pg.text.Label("PAUSED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')

    def draw(self):
        with reset_matrix():
            self.title.draw()

    def event(self, _type, *args, **kwargs):
        if _type == EventType.RESIZE:
            w, h = args

            self.title.x = w/2
            self.title.y = h * .9

    def update(self, dt):
        pass

class InfoPanel:

    def __init__(self, level_name, objs, _map, agents):
        self.level_name = level_name
        self.objectives = objs
        self.map = _map
        self.agents = agents

        self.panel = self.create_panel()
        self.title = self.create_title()
        self.objs = self.create_objectives()
        self.minimap = self.create_minimap()

        # -- minimap images
        player_img = Resources.instance.sprite("minimap_player")
        player_img.width = MINIMAP_AGENT_SIZE
        player_img.height = MINIMAP_AGENT_SIZE
        player_img.anchor_x = player_img.width/2
        player_img.anchor_y = player_img.height/2
        self.minimap_player = pg.sprite.Sprite(player_img)

        enemy_img = Resources.instance.sprite("minimap_enemy")
        enemy_img.width = MINIMAP_AGENT_SIZE
        enemy_img.height = MINIMAP_AGENT_SIZE
        enemy_img.anchor_x = enemy_img.width/2
        enemy_img.anchor_y = enemy_img.height/2

        num_enemies = len([a for a in self.agents if isinstance(a, Enemy)])
        self.minimap_enemies = [pg.sprite.Sprite(enemy_img) for _ in range(num_enemies)]

    def draw(self):
        with reset_matrix():
            self.panel.blit(0, 0)
            self.title.draw()
            self.objs.draw()
            self.minimap.draw()
            self.draw_minimap_agents()

    def update(self, dt):
        # -- update position of agents on minimap
        w, h = self.minimap.width, self.minimap.height
        offx, offy = self.minimap.x - w, self.minimap.y - h
        sx, sy = [mini/_map for mini, _map in zip((w,h), self.map.size())]

        e_idx = 0
        for agent in self.agents:
            px, py = agent.pos
            _x = offx + (px*sx)
            _y = offy + (py*sy)

            if isinstance(agent, Player):
                self.minimap_player.update(x=_x, y=_y)
            elif isinstance(agent, Enemy):
                self.minimap_enemies[e_idx].update(x=_x, y=_y)
                e_idx += 1

    def event(self, _type, *args, **kwargs):
        if _type == EventType.RESIZE:
            self.panel = self.create_panel()
            self.title = self.create_title()
            self.objs = self.create_objectives()
            self.minimap = self.create_minimap()

    def create_panel(self):
        w, h = window.get_size()
        img = pg.image.SolidColorImagePattern((100, 100, 100, 200))
        panel_background = img.create_image(w, h)
        return panel_background

    def create_title(self):
        w, h = window.get_size()
        level_name = pg.text.Label(self.level_name.title(), color=(255, 0, 0, 200),
            font_size=24, x=w/2, y=h*.95, anchor_x='center', anchor_y='center', bold=True)
        return level_name

    def create_objectives(self):
        txt_objs = "".join(["- "+obj+'\n' for obj in self.objectives])
        text = f"""Objectives:\n {txt_objs}"""
        w, h = window.get_size()

        return pg.text.Label(text, color=(255, 255, 255, 200), width=w/3,
            font_size=16, x=15, y=h*.9, anchor_y='top', multiline=True, italic=True)

    def create_minimap(self):
        w, h = window.get_size()

        msx, msy = w*.75, h*.9
        minimap = self.map.make_minimap((msx, msy), (255, 255, 255, 150))
        minimap.image.anchor_x = minimap.image.width
        minimap.image.anchor_y = minimap.image.height
        minimap.x = w
        minimap.y = h*.9
        return minimap

    def draw_minimap_agents(self):
        e_idx = 0
        for agent in self.agents:
            if isinstance(agent, Player):
                self.minimap_player.draw()
            elif isinstance(agent, Enemy):
                self.minimap_enemies[e_idx].draw()
                e_idx += 1


class EditorToolbar:
    WIDTH = 60

    def __init__(self, data):
        # -- toolbar
        self.toolbar_settings = {
            "size" : (self.WIDTH, window.height),
            "color" : (207, 188, 188, 255)
        }
        self.toolbar = pg.image.SolidColorImagePattern(
            self.toolbar_settings.get("color"))
        self.toolbar_image = self.toolbar.create_image(
            *self.toolbar_settings.get("size"))

        # -- tools
        self.tools = [
            AddTileTool(),
            AddAgentTool(),
            AddWaypointTool()
        ]

        self.tool_start_loc = (0, window.height)
        self.tool_settings = {
            "size" : (50, 50),
            "border" : (5, 5),
            "anchor" : (25, 25)
        }
        self.init_tools()
        # -- set data that tools operate on
        for tool in self.tools:
            tool.set_data(data)

    def init_tools(self):
        locx, locy = self.tool_start_loc
        # -- rely on orderd dict
        sz, brd, anch = [val for key, val in self.tool_settings.items()]

        for idx, tool in enumerate(self.tools):
            locx = brd[0] + anch[0]
            locy -= brd[1] + (sz[1] if idx > 0 else 0) + (anch[1] if idx == 0 else 0)
            tool.position = (locx, locy)
            tool.size = self.tool_settings.get("size")

    def get_rect(self):
        center = (self.WIDTH/2, window.height/2)
        size = (self.WIDTH, window.height)
        return [center, size]

    def draw(self):
        self.toolbar_image.blit(0, 0)
        for tool in self.tools:
            tool.draw()

    def update(self, dt):
        for tool in self.tools:
            tool.update(dt)

            if tool.activated:
                # -- set all tools as inactive
                set_flag('is_active', False, self.tools)
                set_flag('activated', False, self.tools)

                # -- activate current tool
                tool.is_active = True

    def event(self, *args, **kwargs):
        for tool in self.tools:
            tool.event(*args, **kwargs)

        # -- handle resize
        _type = args[0]
        if _type == EventType.RESIZE:
            _,_,h = args
            self.tool_start_loc = (0, h)
            self.init_tools()

            self.toolbar_settings['size'] = (60, h)
            self.toolbar_image = self.toolbar.create_image(
                *self.toolbar_settings.get("size"))

        elif _type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args[1:]

            # -- deactivate all tools if click over empty toolbar area
            if btn == mouse.LEFT and mouse_over_rect((x, y), *self.get_rect()):
                # -- check if mouse was clicked over toolbar but not over a tool,
                if not any([mouse_over_rect((x, y), tool.position, tool.size) for tool in self.tools]):
                    # -- set all tools as inactive
                    set_flag('is_active', False, self.tools)
                    set_flag('activated', False, self.tools)

class EditorViewport:
    OFFSET = (EditorToolbar.WIDTH, 0)

    GRID_SIZE = 10000
    GRID_SPACING = 50

    def __init__(self, data):
        self.data = data

        # -- drag options
        self._is_panning = False
        self._pan_offset = (0, 0)

        # -- zoom ptions
        self._zoom = (1, 1)
        self._zoom_sensitivity = 0.1

        # -- map options
        self.wall_img   = Resources.instance.sprite("wall")
        image_set_size(self.wall_img, self.GRID_SPACING, self.GRID_SPACING)

        self.floor_img   = Resources.instance.sprite("floor")
        image_set_size(self.floor_img, self.GRID_SPACING, self.GRID_SPACING)

        # -- player options
        self.player_img = Resources.instance.sprite("hitman1_gun")
        image_set_size(self.player_img, self.GRID_SPACING*.75, self.GRID_SPACING*.75)
        image_set_anchor_center(self.player_img)

        # -- enemy options
        self.enemy_img = Resources.instance.sprite("robot1_gun")
        image_set_size(self.enemy_img, self.GRID_SPACING*.75, self.GRID_SPACING*.75)
        image_set_anchor_center(self.enemy_img)

        self.enemy_target = Resources.instance.sprite("enemy_target")
        image_set_size(self.enemy_target, *(EditorViewport.GRID_SPACING,)*2)
        image_set_anchor_center(self.enemy_target)

    def reload(self):
        self = EditorViewport(self.data)

    def get_rect(self):
        width = window.width - EditorToolbar.WIDTH
        size = (width, window.height)
        center = (
            width/2 + EditorToolbar.WIDTH,
            window.height/2)
        return [center, size]

    @contextmanager
    def _editor_do_pan(self):
        glPushMatrix()
        glTranslatef(*self._pan_offset, 0)
        yield
        glPopMatrix()

    @contextmanager
    def _editor_do_zoom(self):
        glPushMatrix()
        glScalef(*self._zoom, 1)
        yield
        glPopMatrix()

    def _editor_draw_grid(self):
        glLineWidth(2)
        glPushMatrix()
        glTranslatef(EditorToolbar.WIDTH, 0, 0)

        glBegin(GL_LINES)
        for y in range(-self.GRID_SIZE, self.GRID_SIZE, self.GRID_SPACING):
            glColor4f(1, 1, 1, 1)

            # -- vertical lines
            if y == 0:
                glColor4f(0, 0, 1, 1)
            glVertex2f(y, -self.GRID_SIZE)
            glVertex2f(y, self.GRID_SIZE)

            # -- horizontal lines
            if y == 0:
                glColor4f(1, 0, 0, 1)
            glVertex2f(-self.GRID_SIZE, y)
            glVertex2f(self.GRID_SIZE, y)

        glEnd()
        glPopMatrix()

    def _editor_draw_map(self):
        mx, my = self.OFFSET
        for y, row in enumerate(self.data['map']):
            for x, data in enumerate(row):
                offx, offy = x * self.GRID_SPACING, y * self.GRID_SPACING
                if data == "#":
                    self.wall_img.blit(offx+mx, offy+my, 0)
                elif data == ' ':
                    self.floor_img.blit(offx+mx, offy+my, 0)

    def _editor_draw_player(self):
        px, py = self.data['player']
        mx, my = self.OFFSET
        self.player_img.blit(px+mx, py+my, 0)

    def _editor_draw_enemies(self):
        mx, my = self.OFFSET
        for pos in self.data['enemies']:
            px, py = pos
            self.enemy_img.blit(px+mx, py+my, 0)

        enemy_id = self.data.get('_active_enemy')
        if enemy_id:
            ex, ey = self.data['enemies'][enemy_id-1]
            self.enemy_target.blit(ex+mx, ey+my, 0)

    def _editor_draw_waypoints(self):
        waypoints = self.data.get('waypoints')
        if waypoints:
            # -- check if we have active enemy
            enemy_id = self.data.get('_active_enemy')
            if enemy_id:
                # -- select waypoints for active enemy
                points = waypoints[enemy_id-1]

                # -- draw waypoints
                debug_draw_path(points, color=(0,0,1,1))
                for point in points:
                    debug_draw_point(point, color=(1,1,1,1))

    def draw(self):
        with self._editor_do_pan():
            with self._editor_do_zoom():
                # -- draw editor grid
                self._editor_draw_grid()

                # -- draw map data
                self._editor_draw_map()

                # -- draw player
                self._editor_draw_player()

                # -- draw enemies
                self._editor_draw_enemies()

                # -- draw waypoints
                self._editor_draw_waypoints()

    def update(self, dt):
        pass

    def event(self, *args, **kwargs):
        _type = args[0]

        if _type == EventType.MOUSE_DRAG:
            x, y, dx, dy, but, mod = args[1:]
            if not mouse_over_rect((x, y), *self.get_rect()): return

            if but == mouse.MIDDLE:
                self._is_panning = True
                px, py = self._pan_offset
                self._pan_offset = (px+dx, py+dy)
        else:
            self._is_panning = False

        if _type == EventType.MOUSE_SCROLL:
            x, y, sx, sy = args[1:]
            if not mouse_over_rect((x, y), *self.get_rect()): return

            zx, zy = self._zoom
            if sy < 0:
                if zx > .2 and zy > .2:
                    zx -= self._zoom_sensitivity
                    zy -= self._zoom_sensitivity
            else:
                zx += self._zoom_sensitivity
                zy += self._zoom_sensitivity

            self._zoom = (zx, zy)

class EditorToolprops:
    pass


class EditorTool:

    def __init__(self, options):
        # -- options
        # -- e.g {'Add Player' : player_image, 'Add_Enemy' : enemy_image}
        self.options = options
        self.level_data = None

        self.position = (0, 0)
        self.size = (0, 0)

        # -- set image anchors to center:
        for _,img in self.options.items():
            image_set_anchor_center(img)

        self.default = list(options)[0]

        self.tool_background = Resources.instance.sprite("tool_background")
        image_set_anchor_center(self.tool_background)

        self.tool_indicator = Resources.instance.sprite("tool_indicator")
        image_set_anchor_center(self.tool_indicator)

        self.tool_active = Resources.instance.sprite("tool_select")
        image_set_anchor_center(self.tool_active)

        # -- flags to show optional tools
        self.mouse_down_duration = 0
        self.mouse_hold_duration = .5
        self.start_show_event = False
        self.show_options = False

        # -- flags for active state of the tool
        self.is_active = False
        self.activated = False

    def set_data(self, val):
        self.level_data = val

    def draw(self):
        # -- draw tool background
        self.tool_background.blit(*self.position)

        # -- draw default tool
        img = self.options[self.default]
        img.blit(*self.position)

        # -- draw tool indicator
        if len(self.options.items()) > 1:
            # -- draw small arror to indicate more than one option
            if not self.show_options:
                self.tool_indicator.blit(*self.position)

        # -- draw tool active
        if self.is_active:
            self.tool_active.blit(*self.position)

        # -- draw all tool option when mouse held down
        # -- this will be drawn a little off side
        if self.show_options and len(self.options.items()) > 1:
            offx = 50
            for idx, (name, image) in enumerate(self.options.items()):
                idx += 1
                px, py = self.position
                loc = (px + (idx*offx), py)
                self.tool_background.blit(*loc)
                image.blit(*loc)

    def update(self, dt):
        if self.start_show_event:
            self.mouse_down_duration += dt

            if self.mouse_down_duration >= self.mouse_hold_duration:
                self.show_options = True
                self.start_show_event = False
                self.mouse_down_duration = 0

    def event(self, _type, *args, **kwargs):

        if _type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args
            if btn == mouse.LEFT and mouse_over_rect((x, y), self.position, self.size):
                self.start_show_event = True

        if _type == EventType.MOUSE_UP:
            x, y, btn, mod = args
            if btn == mouse.LEFT:
                if self.start_show_event or self.show_options:
                    self.activated = True

                if self.start_show_event:
                    self.start_show_event = False

                if self.show_options:
                    # -- check if mouse was released over a tool option
                    # --  set that tool as active
                    offx = 50
                    for idx, (name, image) in enumerate(self.options.items()):
                        idx += 1
                        px, py = self.position
                        loc = (px + (idx*offx), py)
                        if mouse_over_rect((x,y), loc, self.size):
                            self.default = list(self.options)[idx-1]

                    self.show_options = False

class AddTileTool(EditorTool):
    def __init__(self):
        opts = {
            "Wall" : Resources.instance.sprite("tool_wall"),
            "Floor" : Resources.instance.sprite("tool_floor")
        }
        super(AddTileTool, self).__init__(opts)

    def _mouse_pos_to_map(self, x, y):
        # -- convert mouse position to map array indices
        grid_sp = EditorViewport.GRID_SPACING
        ox, oy = EditorViewport.OFFSET
        return (x-ox) // grid_sp, (y-oy) // grid_sp

    def _mouse_pos_to_grid(self, x, y):
        # -- convert mouse position to grid center position
        grid_sp = EditorViewport.GRID_SPACING
        idx, idy = self._mouse_pos_to_map(x, y)
        return (idx * grid_sp) + grid_sp/2, (idy * grid_sp) + grid_sp/2

    def _map_add_tile(self, idx, idy, data):
        _map = self.level_data.get('map')

        # -- modifiy map list to accomodate new wall
        items_to_add = (idx+1) - len(_map[0])
        rows_to_add = (idy+1) - len(_map)
        len_rows = len(_map[0])

        # -- add new rows
        if rows_to_add:
            for i in range(rows_to_add):
                _map.append(['' for _ in range(len_rows)])

        # -- add new items
        if items_to_add:
            for row in _map:
                    for _ in range(items_to_add):
                        row.append('')

        # -- set wall at target index
        _map[idy][idx] = data

    def _map_add_wall_at(self, idx, idy):
        _map = self.level_data.get('map')
        if _map:
            # -- ensure list contains data
            if idy < len(_map) and idx < len(_map[0]):
                _map[idy][idx] = '#'
            else:
                self._map_add_tile(idx, idy, '#')

    def _map_remove_wall_at(self, idx, idy):
        _map = self.level_data.get('map')
        if _map:
            # -- ensure list contains data
            if idy < len(_map) and idx < len(_map[0]):
                _map[idy][idx] = ''

    def _map_add_floor_at(self, idx, idy):
        _map = self.level_data.get('map')
        if _map:
            # -- ensure list contains data
            if idy < len(_map) and idx < len(_map[0]):
                _map[idy][idx] = ' '
            else:
                self._map_add_tile(idx, idy, ' ')

    def _map_remove_floor_at(self, idx, idy):
        _map = self.level_data.get('map')
        if _map:
            # -- ensure list contains data
            if idy < len(_map) and idx < len(_map[0]):
                _map[idy][idx] = ''

    def event(self, _type, *args, **kwargs):
        super(AddTileTool, self).event(_type, *args, **kwargs)
        if not self.is_active: return

        if _type == EventType.MOUSE_DRAG or _type == EventType.MOUSE_DOWN:
            x,y,*_,but,mod = args
            # -- ensure mouse if over viewport
            if x < EditorToolbar.WIDTH: return

            if but == mouse.LEFT:
                if self.show_options: return # -- showing tool options

                map_id = self._mouse_pos_to_map(x, y)
                if self.default == 'Wall':
                    if mod & key.MOD_CTRL:
                        self._map_remove_wall_at(*map_id)
                    else:
                        self._map_add_wall_at(*map_id)
                elif self.default == 'Floor':
                    if mod & key.MOD_CTRL:
                        self._map_remove_floor_at(*map_id)
                    else:
                        self._map_add_floor_at(*map_id)

class AddAgentTool(EditorTool):
    def __init__(self):
        opts = {
            "Player" : Resources.instance.sprite("tool_player"),
            "Enemy" : Resources.instance.sprite("tool_enemy"),
            # "NPC" : Resources.instance.sprite("tool_npc")
        }
        super(AddAgentTool, self).__init__(opts)

    def event(self, _type, *args, **kwargs):
        super(AddAgentTool, self).event(_type, *args, **kwargs)
        if not self.is_active: return

        if _type == EventType.MOUSE_DOWN:
            x, y, but, mod = args
            # -- ensure mouse if over viewport
            if x < EditorToolbar.WIDTH: return

            if but == mouse.LEFT:
                ox, oy = EditorViewport.OFFSET
                px, py = x-ox, y-oy

                if self.default == 'Player':
                    self.level_data['player'] = (px, py)
                elif self.default == 'Enemy':
                    if mod & key.MOD_CTRL:
                        enemies = self.level_data['enemies']
                        waypoints = self.level_data['waypoints']
                        for idx, en in enumerate(enemies):
                            if mouse_over_rect((px,py), en, (EditorViewport.GRID_SPACING*.75,)*2):
                                self.level_data['enemies'].remove(en)
                                self.level_data['waypoints'].remove(waypoints[idx])
                    else:
                        self.level_data['enemies'].append((px, py))
                        self.level_data['waypoints'].append([])

class AddWaypointTool(EditorTool):
    def __init__(self):
        opts = {
            "Waypoint" : Resources.instance.sprite("tool_waypoint"),
        }
        super(AddWaypointTool, self).__init__(opts)

    def event(self, _type, *args, **kwargs):
        super(AddWaypointTool, self).event(_type, *args, **kwargs)
        if not self.is_active: return

        if _type == EventType.MOUSE_DOWN:
            x, y, but, mod = args

            # -- ensure mouse if over viewport
            if x < EditorToolbar.WIDTH: return

            # -- create waypoint
            if but == mouse.LEFT:
                # -- check if an enemy is selected
                enemy_id = self.level_data.get('_active_enemy')
                if enemy_id:
                    # -- ensure waypoint list exist
                    waypoints = self.level_data.get('_waypoints')
                    if not waypoints:
                        self.level_data['_waypoints'] = []
                        waypoints = self.level_data['_waypoints']

                    # -- check if waypoints exist for all enemies
                    missing = len(self.level_data['enemies']) > len(waypoints)
                    if missing:
                        for _ in range(len(self.level_data['enemies']) - len(waypoints)):
                            waypoints.append([])

                    # -- add mouse location to the selected enemy waypoint
                    waypoints[enemy_id-1].append((x, y))

            # -- select enemy
            elif but == mouse.RIGHT:
                ox, oy = EditorViewport.OFFSET
                px, py = x-ox, y-oy

                if mod & key.MOD_CTRL:
                    del self.level_data['_active_enemy']
                else:
                    enemies = self.level_data['enemies']
                    for idx, en in enumerate(enemies):
                        if mouse_over_rect((px,py), en, (EditorViewport.GRID_SPACING*.75,)*2):
                            self.level_data['_active_enemy'] = idx+1

'''
============================================================
---   FUNCTIONS
============================================================
'''
def angle(p):
    nx, ny = normalize(p)
    return math.degrees(math.atan2(ny, nx))

def normalize(p):
    mag = math.sqrt(distance_sqr((0, 0), p))
    if mag:
        x = p[0] / mag
        y = p[1] / mag
        return (x, y)
    return p

def set_flag(name, value, items):
    for item  in items:
        setattr(item, name, value)

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
        eshape = arbiter.shapes[1]

        normal = pshape.body.position - eshape.body.position
        normal = normal.normalized()
        pshape.body.position = eshape.body.position + (normal * (pshape.radius*2))
        return True

    for etype in ENEMY_TYPES:
        handler = space.add_collision_handler(
                COLLISION_MAP.get("PlayerType"), etype)
        handler.begin = player_enemy_solve

    # Enemy-Enemy Collision
    def enemy_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        eshape  = arbiter.shapes[0]
        eshape1 = arbiter.shapes[1]

        normal = eshape.body.position - eshape1.body.position
        normal = normal.normalized()

        # -- to prevent, dead stop, move eshape a litte perpendicular to collision normal
        perp = pm.Vec2d(normal.y, -normal.x)
        perp_move = perp * (eshape.radius*2)
        eshape.body.position = eshape1.body.position + (normal * (eshape.radius*2)) + perp_move
        return True

    for etype1, etype2 in it.combinations(ENEMY_TYPES, 2):
        handler = space.add_collision_handler(
                etype1, etype2)
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

def image_set_size(img, w, h):
    img.width = w
    img.height = h

def image_set_anchor_center(img):
    img.anchor_x = img.width/2
    img.anchor_y = img.height/2

def mouse_over_rect(mouse, center, size):
    mx, my = mouse
    tx, ty = center
    dx, dy = abs(tx - mx), abs(ty - my)

    tsx, tsy = size
    if dx < tsx/2 and dy < tsy/2:
        return True
    return False

'''
============================================================
---   MAIN
============================================================
'''

# -- create window
window = pg.window.Window(*SIZE, resizable=True)
window.set_minimum_size(*SIZE)
window.set_caption(CAPTION)
window.maximize()

# -- wierd bug - have to push twice
window.push_handlers(KEYS)
window.push_handlers(KEYS)

# -- enemy collision - !! HACK !!
ENEMY_TYPES = []

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
    game.event(EventType.RESIZE, w, h)

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

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    game.event(EventType.MOUSE_DRAG, x, y, dx, dy, button, modifiers)

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    game.event(EventType.MOUSE_SCROLL, x, y, scroll_x, scroll_y)

def on_update(dt):
    phy.update()
    game.update(dt)

if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/FPS)
    pg.app.run()