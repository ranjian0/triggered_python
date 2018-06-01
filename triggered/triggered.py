import sys
import time
import math
import random
import pygame as pg
import pymunk as pm
import itertools as it

from enum          import Enum
from collections   import namedtuple
from pygame.sprite import Sprite, Group
from pygame.math   import Vector2     as vec2
from pymunk        import pygame_util as putils

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
TRANSPARENT = (0, 0, 0, 0)

COLLISION_MAP = {
    "PlayerType" : 1,
    "EnemyType"  : 2,
}

SPACE        = pm.Space()
PHYSICS_STEP = 50
putils.positive_y_is_up = False


def main():
    pg.init()
    pg.display.set_caption(CAPTION)
    screen  = pg.display.set_mode(
        SIZE, pg.RESIZABLE, 32)

    clock   = pg.time.Clock()

    manager = SceneManager()
    manager.add(MainScene, True)
    manager.add(GameScene)
    manager.add(PauseScene)
    manager.add(LevelPassed)
    manager.add(LevelFailed)
    manager.add(GameOver)

    setup_collisions()

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

    # level = LevelManager.instance.get_current()
    # level.MAP.resize()

def add_wall(pos, size):

    shape = pm.Poly.create_box(SPACE.static_body, size=size)
    shape.body.position = pos
    SPACE.add(shape)

def setup_collisions():

    # Player-Enemy Collision
    def player_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        pshape = arbiter.shapes[0]
        eshape  = arbiter.shapes[1]

        normal = pshape.body.position - eshape.body.position
        normal = normal.normalized()
        pshape.body.position = eshape.body.position + (normal * (pshape.radius*2))
        return True

    handler = SPACE.add_collision_handler(
            COLLISION_MAP.get("PlayerType"),
            COLLISION_MAP.get("EnemyType")
        )
    handler.begin = player_enemy_solve

    # Enemy-Enemy Collision
    def enemy_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        eshape  = arbiter.shapes[0]
        eshape1 = arbiter.shapes[1]

        normal = eshape.body.position - eshape1.body.position
        normal = normal.normalized()
        perp   = vec2(normal.y, -normal.x)

        eshape.body.position = eshape.body.position + (perp * (eshape.radius/2))
        return True

    handler = SPACE.add_collision_handler(
            COLLISION_MAP.get("EnemyType"),
            COLLISION_MAP.get("EnemyType")
        )
    handler.begin = enemy_enemy_solve

if __name__ == '__main__':
    main()
