import pymunk as pm
import itertools as it
from pymunk import pygame_util as putils
from pygame.math   import Vector2 as vec2

putils.positive_y_is_up = False

COLLISION_MAP = {
    "PlayerType" : 1,
    "EnemyType"  : 2,
    "WallType"   : 3,
}

class Physics:

    def __init__(self, steps=50):
        self.space = pm.Space()
        self.steps = steps

        setup_collisions(self.space)

    def add(self, *args):
        self.space.add(*args)

    def remove(self, *args):
        self.space.remove(*args)

    def update(self):
        for _ in it.repeat(None, self.steps):
            self.space.step(0.1 / self.steps)

    def debug_draw(self, surf):
        options = putils.DrawOptions(surf)
        self.physics_space.debug_draw(options)

def setup_collisions(space):

    # Player-Enemy Collision
    def player_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        pshape = arbiter.shapes[0]
        eshape  = arbiter.shapes[1]

        normal = pshape.body.position - eshape.body.position
        normal = normal.normalized()
        pshape.body.position = eshape.body.position + (normal * (pshape.radius*2))
        return True

    handler = space.add_collision_handler(
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
        eshape.body.position = eshape1.body.position + (normal * (eshape.radius*2))
        return True

    handler = space.add_collision_handler(
            COLLISION_MAP.get("EnemyType"),
            COLLISION_MAP.get("EnemyType")
        )
    handler.begin = enemy_enemy_solve
