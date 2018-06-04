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
# res     = Resources()
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



    # while True:
    #     # -- events
    #     for event in pg.event.get():
    #         manager.event(event)

    #         if event.type == pg.QUIT:
    #             sys.exit()

    #         if event.type == pg.VIDEORESIZE:
    #             screen = pg.display.set_mode(
    #                 event.size, pg.RESIZABLE)

    #         if event.type == pg.KEYDOWN:
    #             if event.key == pg.K_ESCAPE:
    #                 sys.exit()

    #     # -- draw
    #     screen.fill(BACKGROUND)
    #     manager.draw(screen)
    #     pg.display.flip()

    #     # -- update
    #     dt = clock.tick(60) / 1000
    #     manager.update(dt)

if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/FPS)
    pg.app.run()
