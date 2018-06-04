import sys
import pyglet as pg

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
# manager = SceneManager()
# for scn in init_scenes():
#     manager.add(scn, scn.name == "Main")


@window.event
def on_draw():
    window.clear()

@window.event
def on_resize(w, h):
    print(f"resized {w}, {h}")

def on_update(dt):
    print(dt)


if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/FPS)
    pg.app.run()
