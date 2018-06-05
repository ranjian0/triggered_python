import os
import sys
import pyglet as pg

from pyglet.gl import *
from pyglet.window import key
from collections import defaultdict, namedtuple

from map import Map
from entities import Player

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


class SceneManager:

    def __init__(self, window, resources):
        self.window = window
        self.resource = resources
        self.current = "Main"
        self.data = defaultdict(list)

        self.init_main()

    def switch(self, name):
        if name in SCENES:
            self.current = name


    # -- methods for main scene
    def init_main(self):
        win = self.window

        main_scene = self.data[self.current]
        main_scene.extend([
            pyglet.text.Label('TRIGGERED', font_name='Times New Roman', color=(255, 0, 0, 255),
                          font_size=40, x=win.width//2, y=500,
                          anchor_x='center', anchor_y='center'),

            pyglet.text.Label('PLAY', font_name='Times New Roman',
                          font_size=36, x=win.width//2, y=400,
                          anchor_x='center', anchor_y='center'),

            pyglet.text.Label('QUIT', font_name='Times New Roman',
                          font_size=36, x=win.width//2, y=325,
                          anchor_x='center', anchor_y='center')

        ])

    def draw_main(self):
        for item in self.data['Main']:
            item.draw()

    def update_main(self, dt):
        pass

    # -- methods for game scene
    def init_game(self):
        _map = Map(self.resource.level('test'), self.resource.sprite('wall_image'))
        player = Player(_map['player_position'], (50, 50),
            self.resource.sprite('hitman1_gun'))

        game_scene = self.data['Game']
        game_scene.append(_map)
        game_scene.append(player)

    def draw_game(self):
        for item in self.data['Game']:
            item.draw()

    def update_game(self, dt):
        pass

    def draw(self):
        if self.current == "Main":
            self.draw_main()
        elif self.current == "Pause":
            pass
        elif self.current == "Game":
            self.draw_game()

    def update(self, dt):
        if self.current == "Main":
            self.update_main(dt)
        elif self.current == "Pause":
            pass
        elif self.current == "Game":
            self.update_game(dt)

    def key_press(self, symbol, modifiers):
        if self.current == "Main":
            if symbol == key.SPACE:
                self.init_game()
                self.switch("Game")


    def key_release(self, key, modifiers):
        pass

    def mouse_press(self, x, y, button, modifiers):
        pass

    def mouse_release(self, x, y, button, modifiers):
        pass

    def mouse_motion(self, x, y, dx, dy):
        pass


'''
============================================================
---   MAIN
============================================================
'''

# -- create window
window = pg.window.Window(*SIZE, resizable=True)
window.set_minimum_size(*SIZE)
window.set_caption(CAPTION)

# -- create manager and resources
res     = Resources()
manager = SceneManager(window, res)

background = res.sprite('world_background')

@window.event
def on_draw():
    window.clear()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    background.blit(0, 0)
    manager.draw()

@window.event
def on_resize(w, h):
    # -- resize background
    background.width = w
    background.height = h

@window.event
def on_key_press(key, modifiers):
    manager.key_press(key, modifiers)

@window.event
def on_key_release(key, modifiers):
    manager.key_release(key, modifiers)

@window.event
def on_mouse_press(x, y, button, modifiers):
    manager.mouse_press(x, y, button. modifiers)

@window.event
def on_mouse_release(x, y, button, modifiers):
    manager.mouse_release(x, y, button, modifiers)

@window.event
def on_mouse_motion(x, y, dx, dy):
    manager.mouse_motion(x, y, dx, dy)

def on_update(dt):
    manager.update(dt)

if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/FPS)
    pg.app.run()
