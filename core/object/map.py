import heapq
import operator
import pyglet as pg
import pymunk as pm
import itertools as it
from resources import Resources
from core.physics import PhysicsWorld
from core.utils import image_set_size

tadd = lambda x,y : tuple(map(operator.add, x, y))
tmul = lambda x,y : tuple(map(operator.mul, x, y))
dist_sqr = lambda x,y: sum(map(operator.pow, map(operator.sub, x, y), (2,2)))

class Map(object):
    """ Create map from level data """

    sprites = []
    node_size = (100, 100)
    def __init__(self, data):
        super(Map, self).__init__()
        self.data = [r for r in data if '#' in r]
        self.batch = pg.graphics.Batch()

        self._navmap = Astar(self.data, self.node_size)
        self._generate()

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

    def on_draw(self):
        self.batch.draw()

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
        cf, cost = self._astar_search(self, p1, p2)
        return reconstruct_path(cf, p1, p2)

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

            for next in self._neighbours(current):
                new_cost = cost_so_far[current] + self._cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
