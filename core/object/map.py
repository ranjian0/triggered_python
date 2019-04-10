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

    def _generate_minimap(self, size):
        wall_color = (50, 50, 50, 255)
        background_color = (200, 0, 0, 0)
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

        sp = pg.sprite.Sprite(background)
        sc = min(sx, sy)
        sp.scale_x = sc
        sp.scale_y = sc
        return sp

    def on_draw(self):
        self.batch.draw()

    def on_draw_last(self):
        if self._show_minimap:
            self._minimap_drop.blit(0, 0)
            self._minimap.draw()

    def on_resize(self, w, h):
        minimap_size = tuple(map(operator.mul, (w,h), (.9, .95)))
        self._minimap = self._generate_minimap(minimap_size)

        self._minimap.image.anchor_x = self._minimap.image.width
        self._minimap.image.anchor_y = 0
        self._minimap.x = w
        self._minimap.y = 25

        drop = pg.image.SolidColorImagePattern((100, 100, 100, 200))
        self._minimap_drop = drop.create_image(w, h)

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
        cf, cost = self._astar_search(p1, p2)
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

            for next in self._get_neighbours(current):
                new_cost = cost_so_far[current] + self._get_cost(current, next)
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
