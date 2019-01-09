import math
import pymunk as pm
import pyglet as pg
import itertools as it

from enum import Enum
from pyglet.gl import *
from resources import Resources
from pyglet.window import key, mouse
from contextlib import contextmanager


class EventType(Enum):
    KEY_DOWN     = 1
    KEY_UP       = 2
    MOUSE_DOWN   = 3
    MOUSE_UP     = 4
    MOUSE_MOTION = 5
    MOUSE_DRAG   = 6
    MOUSE_SCROLL = 7
    RESIZE = 8

    TEXT = 9
    TEXT_MOTION = 10
    TEXT_MOTION_SELECT = 11


class TextInput:

    def __init__(self, text, x, y, width):
        self.batch = pg.graphics.Batch()

        self.document = pg.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), dict(color=(0, 0, 0, 255)))
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pg.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=self.batch)
        self.caret = pg.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.add_background(x - pad, y - pad,
                            x + width + pad, y + height + pad)

        # self.text_cursor = window.get_system_mouse_cursor('text')
        self.set_focus()

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

    def add_background(self, x1, y1, x2, y2):
        vert_list = self.batch.add(4, pg.gl.GL_QUADS, None,
                                     ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', [200, 200, 220, 255] * 4))

    def draw(self):
        self.batch.draw()

    def event(self, _type, *args, **kwargs):
        type_map = {
            EventType.MOUSE_MOTION : self._on_mouse_motion,
            EventType.MOUSE_DOWN : self._on_mouse_press,
            EventType.MOUSE_DRAG : self._on_mouse_drag,
            EventType.TEXT : self._on_text,
            EventType.TEXT_MOTION : self._on_text_motion,
            EventType.TEXT_MOTION_SELECT : self._on_text_motion_select
        }
        if _type in type_map.keys():
            type_map[_type](*args, **kwargs)

    def _on_mouse_motion(self, x, y, dx, dy):
        if self.hit_test(x, y):
            window.set_mouse_cursor(self.text_cursor)
        else:
            window.set_mouse_cursor(None)

    def _on_mouse_press(self, x, y, button, modifiers):
        if self.hit_test(x, y):
            self.set_focus()
            self.caret.on_mouse_press(x, y, button, modifiers)
        else:
            self.set_focus(False)

    def _on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.hit_test(x, y):
            self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def _on_text(self, text):
        self.caret.on_text(text)

    def _on_text_motion(self, motion):
        self.caret.on_text_motion(motion)

    def _on_text_motion_select(self, motion):
        self.caret.on_text_motion_select(motion)

    def set_focus(self, focus=True):
        if focus:
            self.caret.visible = True
        else:
            self.caret.visible = False
            self.caret.mark = self.caret.position = 0

class Button(object):

    def __init__(self):
        self._callback = None
        self._callback_args = ()

    def on_click(self, action, *args):
        if callable(action):
            self._callback = action
            self._callback_args = args

    def hover(self, x, y):
        return NotImplementedError()

    def event(self, _type, *args, **kwargs):
        if _type == EventType.MOUSE_MOTION:
            x, y, *_ = args
            self.hover(x,y)

        elif _type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args

            if btn == mouse.LEFT:
                if self.hover(x,y):
                    self._callback(*self._callback_args)

class TextButton(pg.text.Label, Button):

    def __init__(self, *args, **kwargs):
        pg.text.Label.__init__(self, *args, **kwargs)
        Button.__init__(self)

        self._start_color = self.color
        self._hover_color = (200, 0, 0, 255)

    def _set_hcolor(self, val):
        self._hover_color = val
    hover_color = property(fset=_set_hcolor)

    def get_size(self):
        return self.content_width, self.content_height

    def hover(self, x, y):
        center = self.x, self.y
        if mouse_over_rect((x,y), center, self.get_size()):
            self.color = self._hover_color
            return True

        self.color = self._start_color
        return False

class ImageButton(Button):

    def __init__(self, image, position):
        Button.__init__(self)
        self.image = Resources.instance.sprite(image)
        image_set_anchor_center(self.image)

        self.x, self.y = position
        self.sprite = pg.sprite.Sprite(self.image, x=self.x, y=self.y)

    def update(self, px, py):
        self.sprite.update(x=px, y=py)

    def hover(self, x, y):
        center = self.x, self.y
        size = self.sprite.width, self.sprite.height

        if mouse_over_rect((x,y), center, size):
            return True
        return False

    def draw(self):
        self.sprite.draw()


'''
============================================================
---   FUNCTIONS
============================================================
'''

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
        import cProfile, pstats, io
        s = io.StringIO()
        pr = cProfile.Profile()

        pr.enable()
        yield
        pr.disable()

        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats('cumtime')
        # ps.strip_dirs()
        ps.print_stats()

        all_stats = s.getvalue().split('\n')
        self_stats = "".join([line+'\n' for idx, line in enumerate(all_stats)
            if ('triggered' in  line) or (idx <= 4)])
        print(self_stats)
    else:
        yield

@contextmanager
def reset_matrix(w, h):
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1, 1)

    yield

    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def distance_sqr(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx**2 + dy**2

def add_wall(space, pos, size, _type):
    shape = pm.Poly.create_box(space.static_body, size=size)
    shape.collision_type = _type
    shape.body.position = pos
    space.add(shape)

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def random_color():
    r = random.random()
    g = random.random()
    b = random.random()
    return (r, g, b, 1)

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

def setup_collisions(space, enemy_types, player_type):

    # Player-Enemy Collision
    def player_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        pshape = arbiter.shapes[0]
        eshape = arbiter.shapes[1]

        normal = pshape.body.position - eshape.body.position
        normal = normal.normalized()
        pshape.body.position = eshape.body.position + (normal * (pshape.radius*2))
        return True

    for etype in enemy_types:
        handler = space.add_collision_handler(
                player_type, etype)
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

    for etype1, etype2 in it.combinations(enemy_types, 2):
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
