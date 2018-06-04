import sys
import pyglet as pg
from pyglet.gl import *

from resources import Resources
from scenes import (
    SceneManager, init_scenes)

FPS        = 60
SIZE       = (800, 600)
CAPTION    = "Triggered"
BACKGROUND = (100, 100, 100)


# -- create window
window = pg.window.Window(*SIZE, resizable=True)
window.set_minimum_size(*SIZE)
window.set_caption(CAPTION)

# -- create manager and resources
res = Resources()
manager = SceneManager()
for scn in init_scenes():
    manager.add(scn, scn.name == "Main")

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
