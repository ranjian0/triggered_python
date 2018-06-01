import sys
import pygame as pg
import pymunk as pm

from pymunk import pygame_util as putils

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

SPACE        = pm.Space()
PHYSICS_STEP = 50
putils.positive_y_is_up = False


def main():
    pg.init()
    pg.display.set_caption(CAPTION)
    screen  = pg.display.set_mode(
        SIZE, pg.RESIZABLE, 32)

    clock   = pg.time.Clock()

    manager = SceneManager(SPACE)
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
                resize(event, screen)

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if isinstance(manager.current, GameScene):
                        manager.switch(PauseScene.NAME)

        # -- draw
        screen.fill(BACKGROUND)
        manager.draw(screen)
        pg.display.flip()

        # -- update
        dt = clock.tick(60) / 1000
        for _ in range(PHYSICS_STEP):
            SPACE.step(0.1 / PHYSICS_STEP)
        manager.update(dt)

def resize(ev, screen):
    screen = pg.display.set_mode(
        ev.size, pg.RESIZABLE, 32)

if __name__ == '__main__':
    main()
