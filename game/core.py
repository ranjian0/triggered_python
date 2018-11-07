import io
import math
import pstats
import random
import cProfile
import pyglet as pg

from enum import Enum
from pyglet.gl import *
from collections import namedtuple
from contextlib import contextmanager


class EventType(Enum):
    KEY_UP       = 1
    KEY_DOWN     = 2

    MOUSE_UP     = 3
    MOUSE_DOWN   = 4
    MOUSE_DRAG   = 5
    MOUSE_MOTION = 6
    MOUSE_SCROLL = 7

    RESIZE       = 8

    TEXT               = 9
    TEXT_MOTION        = 10
    TEXT_MOTION_SELECT = 11

LevelData = namedtuple("LevelData",
            ["map",
             "player",
             "enemies",
             "waypoints",
             "lights",
             "objectives"])


def clamp(x, _min, _max):
    return max(_min, min(_max, x))

def angle(p):
    nx, ny = normalize(p)
    return math.degrees(math.atan2(ny, nx))

def normalize(p):
    mag = math.hypot(*p)
    if mag:
        x = p[0] / mag
        y = p[1] / mag
        return (x, y)
    return p

def set_flag(name, value, items):
    for item  in items:
        setattr(item, name, value)

@contextmanager
def profile(perform=True):
    if perform:
        s = io.StringIO()
        pr = cProfile.Profile()

        pr.enable()
        yield
        pr.disable()

        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats('cumtime')
        ps.print_stats()

        all_stats = s.getvalue()
        print(all_stats)
    else:
        yield

@contextmanager
def reset_matrix():
    window = get_window()

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window.width, 0, window.height, -1, 1)

    yield

    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def get_window():
    return list(pg.app.windows)[-1]

def distance_sqr(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx**2 + dy**2

def random_color():
    r = random.random()
    g = random.random()
    b = random.random()
    return (r, g, b, 1)

def setup_collisions(space):

    # Player-Enemy Collision
    def player_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        pshape = arbiter.shapes[0]
        eshape = arbiter.shapes[1]

        normal = pshape.body.position - eshape.body.position
        normal = normal.normalized()
        pshape.body.position = eshape.body.position + (normal * (pshape.radius*2))
        return True

    for etype in Enemy.COL_TYPES:
        handler = space.add_collision_handler(
                COLLISION_MAP.get("PlayerType"), etype)
        handler.begin = player_enemy_solve

    # Enemy-Enemy Collision
    def enemy_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        eshape  = arbiter.shapes[0]
        eshape1 = arbiter.shapes[1]

        normal = eshape.body.position - eshape1.body.position
        normal = normal.normalized()

        # -- to prevent, dead stop, move eshape a litte perpendicular to collision normal
        perp = pm.Vec2d(normal.y, -normal.x)
        perp_move = perp * (eshape.radius*2)
        eshape.body.position = eshape1.body.position + (normal * (eshape.radius*2)) + perp_move
        return True

    for etype1, etype2 in it.combinations(Enemy.COL_TYPES, 2):
        handler = space.add_collision_handler(
                etype1, etype2)
        handler.begin = enemy_enemy_solve

def draw_point(pos, color=(1, 0, 0, 1), size=5):
    glColor4f(*color)
    glPointSize(size)

    glBegin(GL_POINTS)
    glVertex2f(*pos)
    glEnd()
    # -- reset color
    glColor4f(1,1,1,1)

def draw_line(start, end, color=(1, 1, 0, 1), width=2):
    glColor4f(*color)
    glLineWidth(width)

    glBegin(GL_LINES)
    glVertex2f(*start)
    glVertex2f(*end)
    glEnd()
    # -- reset color
    glColor4f(1,1,1,1)

def draw_path(points, color=(1, 0, 1, 1), width=5):
    glColor4f(*color)
    glLineWidth(width)

    glBegin(GL_LINE_STRIP)
    for point in points:
        glVertex2f(*point)
    glEnd()
    # -- reset color
    glColor4f(1,1,1,1)

def image_set_size(img, w, h):
    img.width = w
    img.height = h

def image_set_anchor_center(img):
    img.anchor_x = img.width/2
    img.anchor_y = img.height/2

def mouse_over_rect(mouse, center, size):
    mx, my = mouse
    tx, ty = center
    dx, dy = abs(tx - mx), abs(ty - my)

    tsx, tsy = size
    if dx < tsx/2 and dy < tsy/2:
        return True
    return False
