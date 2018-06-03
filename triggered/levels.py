import random
import pygame as pg

from map import Map
from physics import Physics
from entities import (
    Player, Enemy, COLLISION_MAP)

FAILED_EVT = pg.USEREVENT + 1
PASSED_EVT = pg.USEREVENT + 2

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
        self.agents.clear()
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

        player = None
        self.agents = [a for a in self.agents if not hasattr(a, 'dead')]
        has_player = [a for a in self.agents if isinstance(a, Player)]
        if has_player:
            player = has_player[-1]
            self.map.update(dt, player)
        else:
            # -- player died, post level failed
            failed_event = pg.event.Event(FAILED_EVT)
            pg.event.post(failed_event)
            return


        for agent in self.agents:
            if hasattr(agent, 'update'):
                agent.update(dt)

            if hasattr(agent, 'health'):
                if agent.health <= 0:
                    setattr(agent, 'dead', True)
                    self.physics.remove(agent.shape, agent.body)

            if hasattr(agent, 'bullets'):
                # -- collide walls
                for bullet in agent.bullets:
                    for wall in self.map.walls:
                        if bullet.rect.colliderect(wall):
                            bullet.kill()

                # -- player --> enemies
                if isinstance(agent, Player):
                    for e in [a for a in self.agents if isinstance(a, Enemy)]:
                        for b in agent.bullets:
                            if e.rect.colliderect(b.rect):
                                e.hit()
                                b.kill()
                else:
                # -- enemy --> player
                    for bullet in agent.bullets:
                        if player.rect.colliderect(bullet.rect):
                            player.hit()
                            bullet.kill()

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
        self.completed = self.index == len(self.levels) - 1
        if not self.completed:
            self.index += 1
            return self.current()
        return None

    def __iter__(self):
        for l in self.levels:
            yield l

    def draw(self, surface):
        self.current().draw(surface)

    def update(self, dt):
        self.current().update(dt)

    def event(self, ev):
        self.current().event(ev)
