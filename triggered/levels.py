import random
import pygame as pg
from map import Map
from physics import Physics

from entities import Player, Enemy, COLLISION_MAP

class Level:

    def __init__(self, name, data):
        self.name = name
        self.data = self._parse(data)
        self.physics = Physics()

        self.map = None
        self.agents = []
        self.reload()

    def _parse(self, data):
        result = []
        with open(data, 'r') as d:
            for line in d.readlines():
                result.append(list(line.strip()))
        return result

    def reload(self):
        self.map = Map(self.data, physics=self.physics)

        # -- add player to map position
        player = Player(self.map['player_position'], (50, 50), self.physics)
        self.agents.append(player)

        # -- add other agents map positions
        for point in self.map['enemy_position']:
            patrol_points = random.sample(self.map['patrol_positions'],
                random.randint(2, len(self.map['patrol_positions'])//2))

            patrol = self.map.pathfinder.calc_patrol_path([point] + patrol_points)
            e = Enemy(point, (50, 50), patrol, self.physics)
            e.watch_player(player)
            self.agents.append(e)

    def draw(self, surface):
        self.map.draw(surface, self.agents)

    def update(self, dt):
        self.physics.update()
        self.map.update(dt, self.agents)

    def event(self, ev):
        self.map.event(ev, self.agents)

class LevelManager:

    def __init__(self):
        self.levels = []
        self.index = 0

        self.completed = False

    def add(self, levels):
        if isinstance(levels, list):
            self.levels.extend(levels)
        else:
            self.levels.append(levels)

    def current(self):
        return self.levels[self.index]

    def next(self):
        self.completed = self.current < len(self.levels) - 1
        if not self.completed:
            self.current += 1

    def draw(self, surface):
        self.current().draw(surface)

    def update(self, dt):
        self.current().update(dt)

    def event(self, ev):
        self.current().event(ev)
