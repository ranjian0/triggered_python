import os
import sys
import math
import random
import pickle
import pprint as pp
import pyglet as pg
import pymunk as pm
import itertools as it

from utils import *
from enum import Enum
from pyglet.gl import *
from pyglet.window import key, mouse
from contextlib import contextmanager
from pymunk import pyglet_util as putils
from resources import Resources, LevelData
from pyglet.text import layout, caret, document
from collections import defaultdict, namedtuple

FPS        = 60
DEBUG      = 0
SIZE       = (800, 600)
CAPTION    = "Triggered"
BACKGROUND = (100, 100, 100)

KEYMAP = {
    key.W : (0, 1),
    key.S : (0, -1),
    key.A : (-1, 0),
    key.D : (1, 0)
}

RAYCAST_FILTER = 0x1
RAYCAST_MASK = pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS ^ RAYCAST_FILTER)
COLLISION_MAP = {
    "PlayerType" : 1,
    "WallType"   : 2,
    "PlayerBulletType" : 3,
    "EnemyBulletType"  : 4,
    "EnemyType" : 100
}


'''
============================================================
---   CLASSES
============================================================
'''
class GameState(Enum):
    MAINMENU = 1
    RUNNING  = 2
    PAUSED   = 3

class Game:

    def __init__(self):
        self.state = GameState.MAINMENU

        self.manager = LevelManager()
        self.manager.add([
            Level(os.path.basename(l).split('.')[0]) for l in sorted_levels()
        ])

        self.mainmenu = MainMenu()
        self.pausemenu = PauseMenu()

    def start(self):
        self.manager.load()
        self.state = GameState.RUNNING

    def pause(self):
        self.state = GameState.PAUSED

    def draw(self):
        if self.state == GameState.MAINMENU:
            self.mainmenu.draw()
        elif self.state == GameState.PAUSED:
            self.pausemenu.draw()
        elif self.state == GameState.RUNNING:
            self.manager.draw()

    def event(self, *args, **kwargs):
        _type = args[0]

        if self.state == GameState.MAINMENU:
            self.mainmenu.event(*args, **kwargs)

        elif self.state == GameState.PAUSED:
            self.pausemenu.event(*args, **kwargs)
            if _type == EventType.KEY_DOWN:
                if args[1] == key.P:
                    self.state = GameState.RUNNING

        elif self.state == GameState.RUNNING:
            self.manager.event(*args, **kwargs)

            if _type == EventType.KEY_DOWN:
                symbol, mod = args[1:]
                if symbol == key.P:
                    self.pausemenu.reload()
                    self.state = GameState.PAUSED

    def update(self, dt):
        if self.state == GameState.MAINMENU:
            self.mainmenu.update(dt)
        elif self.state == GameState.RUNNING:
            self.manager.update(dt)
        elif self.state == GameState.PAUSED:
            self.pausemenu.update(dt)
        elif self.state == GameState.EDITOR:
            self.editor.update(dt)

class Physics:

    def __init__(self):
        self.space = pm.Space()

    def add(self, *args):
        self.space.add(*args)

    def remove(self, *args):
        self.space.remove(*args)

    def clear(self):
        self.remove(self.space.static_body.shapes)
        for body in self.space.bodies:
            self.remove(body, body.shapes)

    def update(self, dt):
        for _ in it.repeat(None, FPS):
            self.space.step(1. / FPS)

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


class Player(key.KeyStateHandler):

    def __init__(self, position, size, image, _map, physics):
        # --
        self.batch = pg.graphics.Batch()
        self.map = _map
        self.physics = physics

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
        self.muzzle_offset = (self.size[0]/2+Bullet.SIZE/2, -self.size[1]*.21)
        self.muzzle_mag = math.sqrt(distance_sqr((0, 0), self.muzzle_offset))
        self.muzzle_angle = angle(self.muzzle_offset)
        self.ammobar = AmmoBar((10, window.height - (AmmoBar.AMMO_IMG_HEIGHT*1.5)), self.ammo)

        # Create Player Image
        self.image = image
        self.image.width = size[0]
        self.image.height = size[1]
        self.image.anchor_x = size[0]/2
        self.image.anchor_y = size[1]/2
        self.sprite = pg.sprite.Sprite(self.image, x=position[0], y=position[1],
            batch=self.batch)

        # player physics
        self.body = pm.Body(1, pm.inf)
        self.body.position = self.pos
        self.shape = pm.Circle(self.body, size[0]*.45)
        self.shape.collision_type = COLLISION_MAP.get("PlayerType")
        self.shape.filter = pm.ShapeFilter(categories=RAYCAST_FILTER)
        physics.add(self.body, self.shape)

        # -- collision handlers
        physics.add_collision_handler(
                COLLISION_MAP.get("PlayerType"),
                COLLISION_MAP.get("EnemyBulletType"),
                handler_begin = self.collide_enemy_bullet
            )

    def collide_enemy_bullet(self, arbiter, space, data):
        bullet = arbiter.shapes[1]
        bullet.cls_object.destroy()
        space.remove(bullet.body, bullet)
        self.do_damage()
        return False

    def do_damage(self):
        self.health -= self.damage
        if self.health < 0: return
        if self.health > 0:
            self.healthbar.set_value(self.health / self.max_health)
        if self.health == 0:
            self.physics.remove(self.body, self.shape)
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

        b = Bullet((px, py), _dir, self.batch, collision_type=COLLISION_MAP.get("PlayerBulletType"), physics=self.physics)
        self.bullets.append(b)

    def draw(self):
        self.batch.draw()

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
            self.ammobar.set_pos((10, h - (AmmoBar.AMMO_IMG_HEIGHT*1.5)))

    def update(self, dt):
        # -- movements
        dx, dy = 0, 0
        for _key, _dir in KEYMAP.items():
            if self[_key]:
                dx, dy = _dir

        # -- running
        speed = self.speed
        if self[key.LSHIFT] or self[key.RSHIFT]:
            speed *= 2.5

        bx, by = self.body.position
        bx += dx * dt * speed
        by += dy * dt * speed

        self.pos = (bx, by)
        self.body.position = self.pos
        self.physics.space.reindex_shapes_for_body(self.body)
        self.sprite.position = (self.body.position.x, self.body.position.y)

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
        self.player_target = None

        # collision handlers
        physics.add_collision_handler(
                col_type,
                COLLISION_MAP.get("PlayerBulletType"),
                handler_begin = self.collide_player_bullet
            )

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

    def draw(self):
        self.batch.draw()

    def update(self, dt):
        player = self.player_target

        if not player.dead:
            player_distance = distance_sqr(player.pos, self.pos)
            previous_state = self.state

            if player_distance < self.chase_radius**2:
                hit = self.physics.raycast(self.pos, player.pos, 1, RAYCAST_MASK)
                if hit:
                    self.state = EnemyState.PATROL
                else:
                    self.state = EnemyState.CHASE
            else:
                #self.state = EnemyState.PATROL
                if previous_state == EnemyState.CHASE:
                    hit = self.physics.raycast(self.pos, player.pos, 1, RAYCAST_MASK)
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

class Bullet:
    SIZE = 12
    HANDLER_TYPES = []

    def __init__(self, position, direction, batch, speed=500, collision_type=None, physics=None):
        self.physics = physics
        self.pos = position
        self.dir = direction
        self.speed = speed
        self.batch = batch
        self.destroyed = False

        # image
        self.image = Resources.instance.sprite("bullet")
        image_set_size(self.image, self.SIZE, self.SIZE)
        image_set_anchor_center(self.image)
        self.sprite = pg.sprite.Sprite(self.image, x=position[0], y=position[1],
            batch=self.batch)

        angle = math.degrees(-math.atan2(direction[1], direction[0]))
        self.sprite.update(rotation=angle)

        # Bullet physics
        self.body = pm.Body(1, 100)
        self.body.position = self.pos
        self.shape = pm.Circle(self.body, 10)
        self.shape.collision_type = collision_type
        self.shape.filter = pm.ShapeFilter(categories=RAYCAST_FILTER)
        physics.add(self.body, self.shape)

        self.shape.cls_object = self
        if collision_type not in self.HANDLER_TYPES:
            physics.add_collision_handler(
                collision_type,
                COLLISION_MAP.get("WallType"),
                handler_begin = self.collide_wall)

            self.HANDLER_TYPES.append(collision_type)

    def collide_wall(self, arbiter, space, data):
        bullet = arbiter.shapes[0]
        bullet.cls_object.destroy()

        space.remove(bullet.body, bullet)
        return False

    def destroy(self):
        self.sprite.batch = None
        self.destroyed = True

    def update(self, dt):
        bx, by = self.pos
        dx, dy = self.dir

        bx += dx * dt * self.speed
        by += dy * dt * self.speed

        self.pos = (bx, by)
        self.body.position = self.pos
        self.physics.space.reindex_shapes_for_body(self.body)
        self.sprite.position = (self.body.position.x, self.body.position.y)

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
        self.make_map(physics)

        self.pathfinder = PathFinder(self.data, node_size)

    def make_map(self, physics):
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
                    add_wall(physics.space, (offx + nsx/2, offy + nsy/2), (nsx, nsy), COLLISION_MAP.get("WallType"))

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

    def make_minimap(self, size, wall_color=(50, 50, 50, 255),
        background_color=(200, 0, 0, 0)):
        sx, sy = [s/ms for s, ms in zip(size, self.size())]
        nsx, nsy = (self.node_size,)*2

        background_image = pg.image.SolidColorImagePattern(background_color)
        background_image = background_image.create_image(*self.size())
        background = background_image.get_texture()

        wall_image = pg.image.SolidColorImagePattern(wall_color)
        wall_image = wall_image.create_image(nsx//4, nsy//4)
        wall = wall_image.get_texture()

        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                offx, offy = x * nsx, y * nsy
                if data == "#":
                    background.blit_into(wall_image, offx, offy, 0)

                    # -- fill x-gaps
                    if x < len(row)-1 and row[x+1] == '#':
                        for i in range(1,4):
                            ox = offx + (i*(nsx//4))
                            background.blit_into(wall_image, ox, offy, 0)
                    # -- fill y-gaps
                    if y < len(self.data)-1 and self.data[y+1][x] == '#':
                        for i in range(1,4):
                            oy = offy + (i*(nsy//4))
                            background.blit_into(wall_image, offx, oy, 0)


        sp = pg.sprite.Sprite(background)
        sc = min(sx, sy)
        sp.scale_x = sc
        sp.scale_y = sc
        return sp

    def draw(self):
        self.batch.draw()

    def size(self):
        ns = self.node_size
        return (ns * len(self.data[0])), (ns * len(self.data))


class LevelStatus(Enum):
    RUNNING = 1
    FAILED  = 2
    PASSED  = 3

class Level:

    def __init__(self, resource_name):
        self.file = Resources.instance.get_path(resource_name)
        self.data = Resources.instance.level(resource_name)
        self.name = self.data.name

        self.phy = Physics()
        self.map = None
        self.agents = []
        self.status = LevelStatus.RUNNING

    def reload(self):
        if not self.data: return
        self.agents.clear()
        self.phy.clear()

        # -- create HUD and Map
        self.hud = HUD()
        self.map = Map(self.data.map, physics=self.phy)

        # -- add player
        player = Player(self.data.player, (50, 50),
            Resources.instance.sprite("hitman1_gun"), self.map, self.phy)
        self.agents.append(player)
        self.hud.add(player.healthbar)
        self.hud.add(player.ammobar)
        window.push_handlers(player)

        # -- add enemies
        for idx, point in enumerate(self.data.enemies):
            # -- get waypoints
            path = self.data.waypoints[idx]
            reversed_midpath = path[::-1][1:-1]

            e = Enemy(point, (50, 50), Resources.instance.sprite("robot1_gun"),
                path + reversed_midpath, COLLISION_MAP.get("EnemyType") + idx, self.phy)
            Enemy.COL_TYPES.append(COLLISION_MAP.get("EnemyType") + idx)

            if DEBUG:
                e.debug_data = (path, random_color())
            e.watch(player)
            e.set_map(self.map)
            self.agents.append(e)

        # -- register collision types
        setup_collisions(self.phy.space, Enemy.COL_TYPES, COLLISION_MAP.get("PlayerType"))

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
        for agent in self.agents:
            agent.draw()
        self.hud.draw()

        if self.show_info:
            self.infopanel.draw()

        if DEBUG:
            self.phy.debug_draw()
            for agent in self.agents:
                if isinstance(agent, Enemy):
                    path, color = agent.debug_data
                    draw_point(agent.pos, color, 10)
                    draw_path(path, color)

    def update(self, dt):
        if not self.data: return
        self.phy.update(dt)
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
            # print("Player Dead")

        if len(self.get_enemies()) == 0:
            self.status = LevelStatus.PASSED
            # print("level Finished")

        if self.show_info:
            self.infopanel.update(dt)

    def event(self, _type, *args, **kwargs):
        if not self.data: return

        self.infopanel.event(_type, *args, **kwargs)
        for agent in self.agents:
            if hasattr(agent, 'event'):
                agent.event(_type, *args, **kwargs)

        if _type in (EventType.KEY_DOWN, EventType.KEY_UP):
            symbol = args[0]
            if symbol == key.TAB:
                self.show_info = True if (_type == EventType.KEY_DOWN) else False

class LevelManager:

    # -- singleton
    instance = None
    def __new__(cls):
        if LevelManager.instance is None:
            LevelManager.instance = object.__new__(cls)
        return LevelManager.instance

    def __init__(self):
        self.levels = []
        self.index = 0

        self.current = None
        self.completed = False

    def load(self):
        self.current = self.levels[self.index]
        self.current.reload()

    def add(self, levels):
        if isinstance(levels, list):
            self.levels.extend(levels)
        else:
            self.levels.append(levels)

    def next(self):
        self.completed = self.index == len(self.levels) - 1
        if not self.completed:
            self.index += 1
            return self.levels[self.index]
        return None

    def set(self, name):
        for idx, level in enumerate(self.levels):
            if level.name == name:
                self.index = idx
                break

    def __iter__(self):
        for l in self.levels:
            yield l

    def draw(self):
        if self.current:
            self.current.draw()

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def event(self, *args, **kwargs):
        if self.current:
            self.current.event(*args, **kwargs)


class HUD:

    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def draw(self):
        with reset_matrix(window.width, window.height):
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

class MainMenu:

    def __init__(self):
        self.title = pg.text.Label("TRIGGERED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')

        self.quit = TextButton("QUIT", bold=True, font_size=32,
                                anchor_x='center', anchor_y='center')
        self.quit.x = self.quit.content_width
        self.quit.y = self.quit.content_height
        self.quit.hover_color = (255, 255, 0, 255)
        self.quit.on_click(sys.exit)

        self.level_pad = 150
        self.level_options = []
        self.level_batch = pg.graphics.Batch()
        for idx, level in enumerate(LevelManager.instance.levels):
            btn = TextButton(level.name, bold=True, font_size=28,
                                anchor_x='center', anchor_y='center',
                                batch=self.level_batch)
            btn.x = self.level_pad
            btn.y = (window.height*.8)-((idx+1)*btn.content_height)
            btn.hover_color = (200, 0, 0, 255)
            btn.on_click(self.select_level, level.name)

            self.level_options.append(btn)

    def select_level(self, name):
        LevelManager.instance.set(name)
        game.start()

    def draw(self):
        with reset_matrix(window.width, window.height):
            self.title.draw()
            self.quit.draw()
            self.level_batch.draw()

    def event(self, _type, *args, **kwargs):

        if _type == EventType.RESIZE:
            w, h = args

            self.title.x = w/2
            self.title.y = h*.9

            self.quit.x = self.quit.content_width
            self.quit.y = self.quit.content_height

            for idx, txt in enumerate(self.level_options):
                txt.x = self.level_pad
                txt.y = (window.height*.8)-((idx+1)*txt.content_height)

        self.quit.event(_type, *args, **kwargs)
        for option in self.level_options:
            option.event(_type, *args, **kwargs)


    def update(self, dt):
        pass

class PauseMenu:

    def __init__(self):
        self.title = pg.text.Label("PAUSED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')
        actions = {"Resume":self.resume, "Restart":self.restart, "Mainmenu":self.mainmenu}
        self.options = []
        self.options_batch = pg.graphics.Batch()
        for idx, (act, callback) in enumerate(actions.items()):
            btn = TextButton(act, bold=True, font_size=32,
                anchor_x='center', anchor_y='center',
                batch=self.options_batch)
            btn.x = window.width/2
            btn.y = (window.height*.7) - (idx * btn.content_height)

            btn.hover_color = (255, 0, 0, 255)
            btn.on_click(callback)
            self.options.append(btn)

    def resume(self):
        game.state = GameState.RUNNING

    def restart(self):
        LevelManager.instance.load()
        game.state = GameState.RUNNING

    def mainmenu(self):
        game.state = GameState.MAINMENU

    def reload(self, *args):
        self.title.x = window.width/2
        self.title.y = window.height*.9

        for idx, opt in enumerate(self.options):
            opt.x = window.width/2
            opt.y = (window.height*.7) - (idx * opt.content_height)

    def draw(self):
        with reset_matrix(window.width, window.height):
            self.title.draw()
            self.options_batch.draw()

    def event(self, _type, *args, **kwargs):
        if _type == EventType.RESIZE:
            w, h = args
            self.reload()

        for opt in self.options:
            opt.event(_type, *args, **kwargs)

    def update(self, dt):
        pass

class InfoPanel:
    MINIMAP_AGENT_SIZE = 25

    def __init__(self, level_name, objs, _map, agents):
        self.level_name = level_name
        self.objectives = objs
        self.map = _map
        self.agents = agents

        self.reload()

        # -- minimap images
        player_img = Resources.instance.sprite("minimap_player")
        image_set_size(player_img, *(self.MINIMAP_AGENT_SIZE,)*2)
        image_set_anchor_center(player_img)
        self.minimap_player = pg.sprite.Sprite(player_img)

        enemy_img = Resources.instance.sprite("minimap_enemy")
        image_set_size(enemy_img, *(self.MINIMAP_AGENT_SIZE,)*2)
        image_set_anchor_center(enemy_img)

        num_enemies = len([a for a in self.agents if isinstance(a, Enemy)])
        self.minimap_enemies = [pg.sprite.Sprite(enemy_img) for _ in range(num_enemies)]

    def reload(self):
        self.panel = self.create_panel()
        self.title = self.create_title()
        self.objs = self.create_objectives()
        self.minimap = self.create_minimap()

    def draw(self):
        with reset_matrix(window.width, window.height):
            self.panel.blit(0, 0)
            self.title.draw()
            self.objs.draw()
            self.minimap.draw()
            self.draw_minimap_agents()

    def update(self, dt):
        # -- update position of agents on minimap
        w, h = self.minimap.width, self.minimap.height
        offx, offy = self.minimap.x - w, self.minimap.y
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
            self.reload()

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

        pad = 25
        msx, msy = w*.75, h*.9
        minimap = self.map.make_minimap((msx, msy))
        minimap.image.anchor_x = minimap.image.width
        minimap.image.anchor_y = 0
        minimap.x = w
        minimap.y = pad
        return minimap

    def draw_minimap_agents(self):
        e_idx = 0
        for agent in self.agents:
            if isinstance(agent, Player):
                self.minimap_player.draw()
            elif isinstance(agent, Enemy):
                self.minimap_enemies[e_idx].draw()
                e_idx += 1


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
game = Game()

glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_BLEND)

@window.event
def on_draw():
    window.clear()
    glClearColor(.39, .39, .39, 1)

    game.draw()
    if DEBUG and game.state == GameState.RUNNING:
        fps.draw()

@window.event
def on_resize(w, h):
    game.event(EventType.RESIZE, w, h)

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.ESCAPE and game.state in (GameState.RUNNING, GameState.PAUSED):
        if game.state == GameState.RUNNING:
            game.pause()
        elif game.state == GameState.PAUSED:
            game.start()
        return pg.event.EVENT_HANDLED
    elif symbol == key.ESCAPE:
        sys.exit()
    game.event(EventType.KEY_DOWN, symbol, modifiers)

@window.event
def on_key_release(symbol, modifiers):
    game.event(EventType.KEY_UP, symbol, modifiers)

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

@window.event
def on_text(text):
    game.event(EventType.TEXT, text)

@window.event
def on_text_motion(motion):
    game.event(EventType.TEXT_MOTION, motion)

@window.event
def on_text_motion_select(motion):
    game.event(EventType.TEXT_MOTION_SELECT, motion)

def on_update(dt):
    game.update(dt)

if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/FPS)
    with profile(DEBUG):
        pg.app.run()