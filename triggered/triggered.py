import os
import sys
import math
import heapq
import pyglet as pg

from enum import Enum
from pyglet.gl import *
from pyglet.window import key
from pygame.math import Vector2 as vec2
from collections import defaultdict, namedtuple

FPS        = 60
SIZE       = (800, 600)
CAPTION    = "Triggered"
BACKGROUND = (100, 100, 100)

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

Resource = namedtuple("Resource", "name data")

'''
============================================================
---   CLASSES
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
        self.background.width = w
        self.background.height = h

    def draw(self):
        self.background.blit(0, 0)
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

class Player:

    def __init__(self, position, size, image):
        # -- properties
        self.pos    = position
        self.size   = size
        self.health = 100
        self.damage = 10
        self.angle  = 0
        self.speed  = 100

        self.direction = (0, 0)
        self.ammo   = 50
        self.moving = False

        # Create Player Image
        self.image = image
        self.image.width = size[0]
        self.image.height = size[1]
        self.image.anchor_x = size[0]/2
        self.image.anchor_y = size[1]/2
        self.sprite = pg.sprite.Sprite(self.image, x=position[0], y=position[1])

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
            # px, py = self.pos
            # ax, ay = x - px, y - py
            self.angle = vec2(x, y).angle_to(self.pos)
            print(" -- ", self.angle)
            print(x, y, " ----- ", self.pos)

    def update(self, dt):
        self.sprite.update(rotation=self.angle)
        if self.moving:
            dx, dy = self.direction
            self.sprite.x += dx * dt * self.speed
            self.sprite.y += dy * dt * self.speed
            self.pos = self.sprite.position


'''
============================================================
---   MAIN
============================================================
'''

# -- create window
window = pg.window.Window(*SIZE, resizable=True)
window.set_minimum_size(*SIZE)
window.set_caption(CAPTION)

res  = Resources()
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
