import os
import sys
import math
import heapq
import pyglet as pg
# import pymunk as pm

from enum import Enum
from pyglet.gl import *
from pyglet.window import key
# from pymunk import pygame_util as putils
from collections import defaultdict, namedtuple

FPS        = 60
SIZE       = (800, 600)
CAPTION    = "Triggered"
BACKGROUND = (100, 100, 100)

SCENES = [
    "Main",
    "Game",
    "Pause",
    "GameOver"
]

KEYMAP = {
    key.W : (0, 1),
    key.S : (0, -1),
    key.A : (-1, 0),
    key.D : (1, 0)
}

class EventType(Enum):
    KEY_DOWN = 1
    KEY_UP   = 2
    MOUSE_DOWN = 3
    MOUSE_UP   = 4
    MOUSE_MOTION = 5
    RESIZE = 6


'''
============================================================
---   CLASSES
============================================================
'''

Resource = namedtuple("Resource", "name data")

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

class Entity:

    def __init__(self, position, size):
        self.pos  = position
        self.size = size

        self.health = 100
        self.damage = 10

        self.angle  = 0
        self.speed  = 100
        self.direction = (0, 0)

    def set_health(self, val):
        self.health = val

    def set_damage(self, val):
        self.damage = val

    def set_angle(self, val):
        self.angle = val

    def set_speed(self, val):
        self.speed = val

    def hit(self):
        self.health -= self.damage

class Player(Entity):

    def __init__(self, position, size, image):
        Entity.__init__(self, position, size)
        self.ammo   = 50
        self.turret = None

        # Create Player Image
        self.image = image
        self.image.width = size[0]
        self.image.height = size[1]
        self.image.anchor_x = size[0]/2
        self.image.anchor_y = size[1]/2
        self.sprite = pg.sprite.Sprite(self.image, x=position[0], y=position[1])

        #
        self.moving = False

    def draw(self):
        self.sprite.draw()

    def event(self, type, *args, **kwargs):
        if type == EventType.KEY_DOWN:
            symbol, mod = args
            if symbol in [key.W, key.A, key.S, key.D]:
                self.moving = True
                self.direction = KEYMAP[symbol]

        elif type == EventType.KEY_UP:
            symbol, mod = args
            if symbol in [key.W, key.A, key.S, key.D]:
                self.moving = False

        elif type == EventType.MOUSE_MOTION:
            x, y, dx, dy = args
            # - calc rotation
            px, py = self.pos
            ax, ay = x - px, y - py
            self.angle = math.degrees(math.atan2(ay, ax))


    def update(self, dt):
        self.sprite.update(rotation=self.angle)
        if self.moving:
            dx, dy = self.direction
            self.sprite.x += dx * dt * self.speed
            self.sprite.y += dy * dt * self.speed
            self.pos = self.sprite.position

class Map:

    def __init__(self, data,
                    wall_img  = None,
                    node_size = 100):
                    #physics   = None):

        self.data       = data
        self.node_size  = node_size
        self.wall_img   = wall_img
        self.wall_img.width = node_size//2
        self.wall_img.height = node_size//2
        # self.physics    = physics

        self.sprites    = []
        self.batch      = pg.graphics.Batch()
        self.make_map()

        self.pathfinder = PathFinder(data, node_size)
        self.spawn_data = self.parse_spawn_points()

    def make_map(self):
        nsx, nsy = (self.node_size,)*2
        sx = (len(self.data[0]) * nsx) - nsx/2
        sy = (len(self.data) * nsy) - nsy/2


        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                if data == "#":
                    offx, offy = x * nsx, y * nsy
                    sp = pg.sprite.Sprite(self.wall_img, x=offx, y=offy, batch=self.batch)
                    self.sprites.append(sp)

                    # Fill gaps
                    # -- gaps along x-axis
                    if x < len(row) - 1 and self.data[y][x + 1] == "#":
                        sp = pg.sprite.Sprite(self.wall_img, x=offx + nsx/2, y=offy, batch=self.batch)
                        self.sprites.append(sp)


                    # -- gaps along y-axis
                    if y < len(self.data) - 1 and self.data[y + 1][x] == "#":
                        sp = pg.sprite.Sprite(self.wall_img, x=offx, y=offy + nsy/2, batch=self.batch)
                        self.sprites.append(sp)

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

    def draw(self):
        self.batch.draw()

    def update(self, dt, player):
        pass

    def __getitem__(self, val):
        return self.spawn_data.get(val, None)

def add_wall(space, pos, size):
    shape = pm.Poly.create_box(space.static_body, size=size)
    shape.body.position = pos
    space.add(shape)

class PathFinder:

    def __init__(self, map_data, node_size):
        self.data = map_data
        self.node_size = (node_size,)*2

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

        # -- find all walkable nodes
        walkable = [mul((x, y), self.node_size) for y, data in enumerate(self.data)
            for x, d in enumerate(data) if d != '#']

        # -- find neighbours that are walkable
        directions      = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neigh_positions = [add(p, mul(d, self.node_size)) for d in directions]
        return [n for n in neigh_positions if n in walkable]

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

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

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



'''
============================================================
---   MAIN
============================================================
'''

class Game:

    def __init__(self, win, res):
        self.window = win
        self.resource = res

        self.background = res.sprite('world_background')
        self.player = Player((200, 300), (50, 50),
            self.resource.sprite('hitman1_gun'))


    def resize(self, w, h):
        pass

    def draw(self):
        # self.background.blit(0, 0)
        self.player.draw()

    def event(self, *args, **kwargs):
        self.player.event(*args, **kwargs)

    def update(self, dt):
        self.player.update(dt)

        # scroll viewport
        px, py = self.player.pos
        w, h = self.window.get_size()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-px + w/2, -py + h/2, 0)


# -- create window
window = pg.window.Window(*SIZE, resizable=True)
window.set_minimum_size(*SIZE)
window.set_caption(CAPTION)

# -- init resource
res = Resources()

game = Game(window, res)

@window.event
def on_draw():
    window.clear()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    game.draw()

@window.event
def on_resize(w, h):
    game.resize(w, h)

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
    game.update(dt)

if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/FPS)
    pg.app.run()
