import pymunk as pm
import itertools as it
from pymunk import pygame_util as putils

putils.positive_y_is_up = False


class Physics:

    def __init__(self, steps=50):
        self.space = pm.Space()
        self.steps = steps


    # -- PUBLIC API
    def add(self, *args):
        self.space.add(*args)

    def remove(self, *args):
        self.space.remove(*args)

    def update(self):
        for _ in it.repeat(None, self.steps):
            self.space.step(0.1 / self.steps)

