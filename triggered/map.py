import heapq
import pygame as pg
import pymunk as pm

from entities import Player
from pymunk import pygame_util as putils

class Map:

    def __init__(self, data,
                    fg        = pg.Color(77,77,77),
                    bg        = pg.Color(120, 95, 50),
                    node_size = 100,
                    physics   = None):

        self.data       = data
        self.node_size  = node_size
        self.foreground = fg
        self.background = bg
        self.physics    = physics

        self.walls      = []
        self.surface    = self.make_map()
        self.rect       = self.surface.get_rect(topleft=(1, 1))

        self.viewport   = None

        self.pathfinder = PathFinder(data, node_size)
        self.spawn_data = self.parse_spawn_points()

    def resize(self):
        display  = pg.display.get_surface()
        self.viewport = display.get_rect().copy()

    def make_map(self):
        nsx, nsy = (self.node_size,)*2
        sx = (len(self.data[0]) * nsx) - nsx/2
        sy = (len(self.data) * nsy) - nsy/2

        surf = pg.Surface((sx, sy)) #.convert_alpha()
        surf.fill(self.background)


        wall_edge_col = pg.Color(26, 26, 26)
        wall_edge_thk = 3

        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                if data == "#":
                    offx, offy = x * nsx, y * nsy
                    r = pg.draw.rect(surf, self.foreground, [offx, offy, nsx/2, nsy/2])
                    pg.draw.rect(surf, wall_edge_col, [offx, offy, nsx/2, nsy/2], wall_edge_thk)
                    self.walls.append(r)
                    add_wall(self.physics.space, r.center, (nsx/2, nsy/2))

                    # Fill gaps
                    # -- gaps along x-axis
                    if x < len(row) - 1 and self.data[y][x + 1] == "#":
                        r = pg.draw.rect(surf, self.foreground, [offx + nsx/2, offy, nsx/2, nsy/2])
                        pg.draw.rect(surf, wall_edge_col, [offx + nsx/2, offy, nsx/2, nsy/2], wall_edge_thk)
                        self.walls.append(r)
                        add_wall(self.physics.space, r.center, (nsx/2, nsy/2))


                    # -- gaps along y-axis
                    if y < len(self.data) - 1 and self.data[y + 1][x] == "#":
                        r = pg.draw.rect(surf, self.foreground, [offx, offy + nsy/2, nsx/2, nsy/2])
                        pg.draw.rect(surf, wall_edge_col, [offx, offy + nsy/2, nsx/2, nsy/2], wall_edge_thk)
                        self.walls.append(r)
                        add_wall(self.physics.space, r.center, (nsx/2, nsy/2))

        return surf

    def parse_spawn_points(self):
        spawn_data = {
            'player_position' : None,   # identifier == 'p'
            'enemy_position'  : [],     # identifier == 'e'
            'mino_position'   : None,   # identifier == 'm'
            'vip_position'    : None,   # identifier == 'v'
            'time_stone'      : None,   # identifier == 't'

            'patrol_positions': [],     # anything but '#', used for enemy patrol
        }

        nsx, nsy = (self.node_size,)*2
        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                location = (x*nsx, y*nsy)

                if   data == "p":
                    spawn_data['player_position'] = location
                elif data == 'e':
                    spawn_data['enemy_position'].append(location)
                elif data == 'm':
                    spawn_data['mino_position'] = location
                elif data == 'v':
                    spawn_data['vip_position'] = location
                elif data == 't':
                    spawn_data['time_stone'] = location

                if data != '#':
                    spawn_data['patrol_positions'].append(location)
        return spawn_data

    def draw(self, surface, entities):
        new_img = self.surface.copy()

        for ent in entities:
            if hasattr(ent, 'draw'):
                ent.draw(new_img)

        surface.blit(new_img, (0, 0), self.viewport)

    def update(self, dt, entities):
        player = None
        entities = [e for e in entities if not hasattr(e, 'dead')]
        for ent in entities:
            if hasattr(ent, 'update'):
                ent.update(dt)

            if hasattr(ent, 'health'):
                if ent.health <= 0:
                    ent.kill()
                    setattr(ent, 'dead', True)
                    self.physics.remove(ent.shape, ent.body)

            if isinstance(ent, Player):
                player = ent

            if hasattr(ent, 'bullets'):
                for bullet in ent.bullets:
                    for wall in self.walls:
                        if bullet.rect.colliderect(wall):
                            bullet.kill()

        if not player: return
        display  = pg.display.get_surface()
        self.viewport = display.get_rect().copy()

        self.viewport.center = player.rect.center
        self.viewport.clamp_ip(self.rect)
        player.viewport = self.viewport

        # Clamp player to map
        player.rect.clamp_ip(self.rect)

    def event(self, ev, entities):
        for ent in entities:
            if hasattr(ent, 'event'):
                ent.event(ev)

    def __getitem__(self, val):
        return self.spawn_data.get(val, None)

def add_wall(space, pos, size):
    shape = pm.Poly.create_box(space.static_body, size=size)
    shape.body.position = pos
    space.add(shape)


class PathFinder:

    def __init__(self, map_data, node_size):
        self.data = map_data
        self.node_size = (node_size,)*2

    def calculate_path(self, p1, p2):
        cf, cost = a_star_search(self, p1, p2)
        return reconstruct_path(cf, p1, p2)

    def calc_patrol_path(self, points):
        result = []
        circular_points = points + [points[0]]
        for i in range(len(circular_points)-2):
            f, s = circular_points[i:i+2]
            path = self.calculate_path(f, s)[1:]
            result.extend(path)
        return result

    def neighbours(self, p):
        add = lambda p1, p2 : (p1[0]+p2[0], p1[1]+p2[1])
        mul = lambda p1, p2 : (p1[0]*p2[0], p1[1]*p2[1])

        # -- find all walkable nodes
        walkable = [mul((x, y), self.node_size) for y, data in enumerate(self.data)
            for x, d in enumerate(data) if d != '#']

        # -- find neighbours that are walkable
        directions      = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neigh_positions = [add(p, mul(d, self.node_size)) for d in directions]
        return [n for n in neigh_positions if n in walkable]

    def cost(self, *ignored):
        return 1

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(graph, start, goal):
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

        for next in graph.neighbours(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.append(start)
    path.reverse()
    return path
