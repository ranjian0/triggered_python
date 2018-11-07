import sys
import enum
import pyglet as pg
from pyglet.gl import *
from pyglet.window import key

from .signal    import connect
from .resource  import Resources
from .editor    import LevelEditor
from .core      import EventType, profile
from .gui       import MainMenu, PauseMenu
from .level     import Level, LevelManager
from .settings  import FPS, LEVELS, DEBUG

SIZE       = (800, 600)
CAPTION    = "Triggered"
BACKGROUND = (100, 100, 100)

class GameState(enum.Enum):
    MAINMENU = 1
    RUNNING  = 2
    PAUSED   = 3
    EDITOR   = 4

class Game:

    def __init__(self):
        self.state = GameState.MAINMENU

        self.editor = LevelEditor()
        self.manager = LevelManager()
        self.manager.add([
                Level(name, file) for name, file in LEVELS
            ])

        self.mainmenu = MainMenu()
        self.pausemenu = PauseMenu()

        connect("start_game", self, "start")

    def start(self, level_name):
        self.manager.set(level_name)
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
        elif self.state == GameState.EDITOR:
            self.editor.draw()

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

                if symbol == key.E and mod & key.MOD_CTRL:
                    self.editor.load(self.manager.current)
                    self.state = GameState.EDITOR

        elif self.state == GameState.EDITOR:
            self.editor.event(*args, **kwargs)

            if _type == EventType.KEY_DOWN:
                symbol, mod = args[1:]

                if symbol == key.E and mod & key.MOD_CTRL:
                    self.editor.save()
                    self.state = GameState.RUNNING

    def update(self, dt):
        if self.state == GameState.MAINMENU:
            self.mainmenu.update(dt)
        elif self.state == GameState.RUNNING:
            self.manager.update(dt)
        elif self.state == GameState.PAUSED:
            self.pausemenu.update(dt)
        elif self.state == GameState.EDITOR:
            self.editor.update(dt)


def start_game():
    game.start()

# -- create window
window = pg.window.Window(*SIZE, resizable=True)
window.set_minimum_size(*SIZE)
window.set_caption(CAPTION)
window.maximize()

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

def main():
    pg.clock.schedule_interval(on_update, 1/FPS)
    with profile(DEBUG):
        pg.app.run()