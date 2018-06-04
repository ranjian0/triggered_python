import sys
import pygame as pg

from resources import Resources
from scenes import (
    SceneManager, init_scenes)


SIZE        = (800, 600)
CAPTION     = "Triggered"
BACKGROUND  = (100, 100, 100)

def main():
    pg.init()
    pg.display.set_caption(CAPTION)

    clock   = pg.time.Clock()
    screen  = pg.display.set_mode(
        SIZE, pg.RESIZABLE, 32)

    res     = Resources()
    manager = SceneManager()
    for scn in init_scenes():
        args = (scn, True) if scn.name == "Main" else (scn, False)
        manager.add(*args)

    while True:
        # -- events
        for event in pg.event.get():
            manager.event(event)

            if event.type == pg.QUIT:
                sys.exit()

            if event.type == pg.VIDEORESIZE:
                screen = pg.display.set_mode(
                    event.size, pg.RESIZABLE, 32)

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()

        # -- draw
        screen.fill(BACKGROUND)
        manager.draw(screen)
        pg.display.flip()

        # -- update
        dt = clock.tick(60) / 1000
        manager.update(dt)

if __name__ == '__main__':
    main()
