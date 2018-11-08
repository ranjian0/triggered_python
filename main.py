import sys
import pyglet as pg
from pyglet.gl import *
from pyglet.window import key

from game import Game, GameState
from game.core import EventType, profile
from game.settings  import FPS, DEBUG, SIZE, CAPTION

# -- create window
window = pg.window.Window(*SIZE, resizable=True)
window.set_minimum_size(*SIZE)
window.set_caption(CAPTION)
window.maximize()

fps  = pg.window.FPSDisplay(window)
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

if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/FPS)
    with profile(False):
        pg.app.run()
