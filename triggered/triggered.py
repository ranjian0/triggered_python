import sys
import pygame as pg

from scenes import (
    SceneManager,
    MainScene,
    GameScene,
    PauseScene,
    LevelPassed,
    LevelFailed,
    GameOver)

SIZE        = (800, 600)
CAPTION     = "Triggered"
BACKGROUND  = (100, 100, 100)

def main():
    pg.init()
    pg.display.set_caption(CAPTION)

    clock   = pg.time.Clock()
    screen  = pg.display.set_mode(
        SIZE, pg.RESIZABLE, 32)

    manager = SceneManager()
    manager.add(MainScene, True)
    manager.add(GameScene)
    manager.add(PauseScene)
    manager.add(LevelPassed)
    manager.add(LevelFailed)
    manager.add(GameOver)

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
