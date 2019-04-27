#  Copyright 2019 Ian Karanja <karanjaichungwa@gmail.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import heapq
import operator
import pyglet as pg
import pymunk as pm
import itertools as it
from resources import Resources
from core.app import Application
from core.physics import PhysicsWorld
from core.utils import (
    reset_matrix,
    image_set_size,
    )
from core.math import (
    tadd,
    tmul,
    dist_sqr,
    heuristic,
    )


class Map(object):
    """ Create map from level data """

    # -- singleton
    instance = None
    def __new__(cls, *args):
        if Map.instance is None:
            Map.instance = object.__new__(cls)
        return Map.instance

    sprites = []
    node_size = (100, 100)
    def __init__(self, data):
        super(Map, self).__init__()
        self.data = [r for r in data if '#' in r]
        self.batch = pg.graphics.Batch()

        self._minimap = None
        self._minimap_drop = None
        self._show_minimap = False
        self._navmap = Astar(self.data, self.node_size)
        self._generate()
        self._generate_minimap()

    def _get_size(self):
        nx, ny = self.node_size
        return nx * len(self.data[0]), ny * len(self.data)
    size = property(_get_size)

    def _generate(self):
        wall_img = Resources.instance.sprite('wall')
        image_set_size(wall_img, *self.node_size)
        floor_img = Resources.instance.sprite('floor')
        image_set_size(floor_img, *self.node_size)

        self.sprites.clear()
        nx, ny = self.node_size
        sx, sy = len(self.data[0]), len(self.data)
        for (ix, iy) in it.product(range(sx), range(sy)):
            data   = self.data[iy][ix]
            px, py = tmul((ix, iy), self.node_size)
            if data:
                sp = pg.sprite.Sprite(wall_img if data == '#' else floor_img,
                        x=px, y=py, batch=self.batch)
                self.sprites.append(sp)

                if data == '#':
                    # -- add collision box
                    world = PhysicsWorld.instance
                    wall = pm.Poly.create_box(world.space.static_body, size=self.node_size)
                    wall.body.position = (px + nx/2, py + ny/2)
                    world.add(wall)

    def _generate_minimap(self):
        wall_color = (50, 50, 50, 255)
        background_color = (200, 0, 0, 0)
        w, h = Application.instance.size
        size = tuple(map(operator.mul, (w,h), (.9, .95)))

        sx, sy = [s/ms for s, ms in zip(size, self.size)]
        nsx, nsy = self.node_size

        background_image = pg.image.SolidColorImagePattern(background_color)
        background_image = background_image.create_image(*self.size)
        background = background_image.get_texture()

        wall_image = pg.image.SolidColorImagePattern(wall_color)
        wall_image = wall_image.create_image(nsx//4, nsy//4)
        wall = wall_image.get_texture()

        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                offx, offy = x * nsx, y * nsy
                if data == "#":
                    background.blit_into(wall_image, offx, offy, 0)

                    # -- fill x-gaps
                    if x < len(row)-1 and row[x+1] == '#':
                        for i in range(1,4):
                            ox = offx + (i*(nsx//4))
                            background.blit_into(wall_image, ox, offy, 0)
                    # -- fill y-gaps
                    if y < len(self.data)-1 and self.data[y+1][x] == '#':
                        for i in range(1,4):
                            oy = offy + (i*(nsy//4))
                            background.blit_into(wall_image, offx, oy, 0)

        sc = min(sx, sy)
        self._minimap = pg.sprite.Sprite(background)
        self._minimap.scale_x = sc
        self._minimap.scale_y = sc

        self._minimap.image.anchor_x = self._minimap.image.width
        self._minimap.image.anchor_y = 0
        self._minimap.x = w
        self._minimap.y = 25

        drop = pg.image.SolidColorImagePattern((100, 100, 100, 200))
        self._minimap_drop = drop.create_image(w, h)

    def on_draw(self):
        self.batch.draw()

    def on_draw_last(self):
        if self._show_minimap:
            with reset_matrix(*self._window_size):
                self._minimap_drop.blit(0, 0)
                self._minimap.draw()

    def on_resize(self, w, h):
        self._generate_minimap()

    def on_key_press(self, symbol, mod):
        if symbol == pg.window.key.TAB:
            self._show_minimap = True

    def on_key_release(self, symbol, mod):
        if symbol == pg.window.key.TAB:
            self._show_minimap = False

    def find_path(self, p1, p2):
        return self._navmap.calculate_path(p1, p2)

    def find_closest_node(self, p):
        return self._navmap.closest_node(p)


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

class Astar:

    def __init__(self, data, node_size):
        self.data = data
        self.node_size = node_size

        self._walkable = self._get_walkable_nodes()

    def calculate_path(self, p1, p2):
        """ Calculate path of walkable nodes from p1 to p2 """
        return self._astar_search(p1, p2)

    def closest_node(self, p):
        data = [(dist_sqr(p, point), point) for point in self._walkable]
        return min(data, key=lambda d:d[0])[1]

    def _get_walkable_nodes(self):
        """ Find all node positions without a wall """
        hns = (self.node_size[0]/2, self.node_size[1]/2)
        walkable = [tadd(hns, tmul((x, y), self.node_size))
            for y, data in enumerate(self.data)
            for x, d in enumerate(data) if d == ' ']
        return walkable

    def _get_neighbours(self, p):
        """ Find all neightbours of p that are walkable"""
        directions      = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neigh_positions = [tadd(p, tmul(d, self.node_size)) for d in directions]
        return [n for n in neigh_positions if n in self._walkable]

    def _get_cost(self, *ignored):
        return 1

    def _astar_search(self, start, goal):
        """ Use astar algorithm to calculate path from start to goal """
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for _next in self._get_neighbours(current):
                new_cost = cost_so_far[current] + self._get_cost(current, _next)
                if _next not in cost_so_far or new_cost < cost_so_far[_next]:
                    cost_so_far[_next] = new_cost
                    priority = new_cost + heuristic(goal, _next)
                    frontier.put(_next, priority)
                    came_from[_next] = current

        return self._reconstruct_path(came_from, start, goal)

    def _reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
