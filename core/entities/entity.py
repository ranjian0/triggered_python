import pyglet as pg
import pymunk as pm

class Entity(object):

    # -- movement
    position : tuple = (0, 0)
    rotation : float = 0.0
    size : float = 1.0

    speed : float = 0.0
    velocity : tuple = (0, 0)

    # -- health
    health : int = 100
    max_health : int = 100
    min_health : int = 0
    damage : int = 5

    # -- collision
    physics_body  : pm.Body   = pm.Body(1, pm.inf)
    physics_shape : pm.Circle = pm.Circle(physics_body, size[0])
    physics_layer : int = 0
    physics_mask  : int = 0

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

