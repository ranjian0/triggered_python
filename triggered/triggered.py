import sys
import pyglet as pg

from resources import Resources
from scenes import (
    SceneManager, init_scenes)


SIZE        = (800, 600)
CAPTION     = "Triggered"
BACKGROUND  = (100, 100, 100)

def main():
    window = pg.window.Window()

    @window.event
    def on_draw():
        window.clear()

    pg.app.run()
    # pg.init()
    # pg.display.set_caption(CAPTION)

    # clock   = pg.time.Clock()
    # screen  = pg.display.set_mode(
    #     SIZE, pg.RESIZABLE)

    # res     = Resources()
    # manager = SceneManager()
    # for scn in init_scenes():
    #     manager.add(scn, scn.name == "Main")

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
    main()
