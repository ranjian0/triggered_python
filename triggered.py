import os
import sys
import math
import heapq
import random
import pickle
import pprint as pp
import pyglet as pg
import pymunk as pm
import operator as op
import itertools as it

from enum import Enum
from pyglet.gl import *
from pyglet.window import key, mouse
from contextlib import contextmanager
from pymunk import pyglet_util as putils
from pyglet.text import layout, caret, document
from collections import defaultdict, namedtuple

FPS        = 60
DEBUG      = 1
SIZE       = (800, 600)
CAPTION    = "Triggered"
BACKGROUND = (100, 100, 100)

KEYMAP = {
    key.W : (0, 1),
    key.S : (0, -1),
    key.A : (-1, 0),
    key.D : (1, 0)
}

RAYCAST_FILTER = 0x1
RAYCAST_MASK = pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS ^ RAYCAST_FILTER)
COLLISION_MAP = {
    "PlayerType" : 1,
    "WallType"   : 2,
    "PlayerBulletType" : 3,
    "EnemyBulletType"  : 4,
    "EnemyType" : 100
}

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

Resource  = namedtuple("Resource", "name data")
LevelData = namedtuple("LevelData",
            ["map",
             "player",
             "enemies",
             "waypoints",
             "lights",
             "objectives"])

'''
============================================================
---   CLASSES
============================================================
'''


class HUD:

    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def draw(self):
        with reset_matrix():
            for item in self.items:
                item.draw()

    def event(self, *args, **kwargs):
        for item in self.items:
            if hasattr(item, 'event'):
                item.event(*args, **kwargs)

class HealthBar:

    def __init__(self, position):
        self.pos = position
        self.batch = pg.graphics.Batch()

        border = Resources.instance.sprite("health_bar_border")
        border.anchor_y = border.height
        self.border = pg.sprite.Sprite(border, x=position[0], y=position[1], batch=self.batch)

        self.bar_im = Resources.instance.sprite("health_bar")
        self.bar_im.anchor_y = self.bar_im.height
        self.bar = pg.sprite.Sprite(self.bar_im, x=position[0], y=position[1], batch=self.batch)

    def draw(self):
        self.batch.draw()

    def set_value(self, percent):
        region = self.bar_im.get_region(0, 0,
            int(self.bar_im.width*percent), self.bar_im.height)
        region.anchor_y = self.bar_im.height
        self.bar.image = region

    def set_pos(self, pos):
        self.pos = pos
        self.border.update(x=pos[0], y=pos[1])
        self.bar.update(x=pos[0], y=pos[1])

class AmmoBar:
    AMMO_IMG_HEIGHT = 30

    def __init__(self, position, ammo):
        self.pos = position
        self.batch = pg.graphics.Batch()
        self.ammo = ammo

        self.ammo_img = Resources.instance.sprite("ammo_bullet")
        image_set_size(self.ammo_img, self.AMMO_IMG_HEIGHT//3, self.AMMO_IMG_HEIGHT)
        self.ammo_img.anchor_y = self.ammo_img.height
        self.bullets = [pg.sprite.Sprite(self.ammo_img, batch=self.batch)
            for _ in range(ammo // 100)]

        self.ammo_text = pg.text.Label(f" X {self.ammo}", bold=True,
            font_size=12, color=(200, 200, 0, 255), batch=self.batch,
            anchor_y='top', anchor_x='left')

        self.set_pos(position)

    def draw(self):
        self.batch.draw()

    def set_value(self, val):
        self.ammo = val

        num_bul = self.ammo // 100
        if len(self.bullets) > num_bul:
            self.bullets.pop(len(self.bullets)-1)
            self.set_pos(self.pos)

        self.ammo_text.text = f" X {val}"

    def set_pos(self, pos):
        self.pos = pos

        px, py = pos
        offx = self.ammo_img.width + 2
        for idx, bull in enumerate(self.bullets):
            bull.x = px + (idx * offx)
            bull.y = py

        txt_off = px + (len(self.bullets) * offx)
        self.ammo_text.x = txt_off
        self.ammo_text.y = py

class MainMenu:

    def __init__(self):
        self.title = pg.text.Label("TRIGGERED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')

        self.quit = TextButton("QUIT", bold=True, font_size=32,
                                anchor_x='center', anchor_y='center')
        self.quit.x = self.quit.content_width
        self.quit.y = self.quit.content_height
        self.quit.hover_color = (255, 255, 0, 255)
        self.quit.on_click(sys.exit)

        self.level_options = []
        self.level_batch = pg.graphics.Batch()
        for idx, level in enumerate(LevelManager.instance.levels):
            btn = TextButton(level.name, bold=True, font_size=28,
                                anchor_x='center', anchor_y='center',
                                batch=self.level_batch)
            btn.x = window.width/4
            btn.y = (window.height*.8)-((idx+1)*btn.content_height)
            btn.hover_color = (200, 0, 0, 255)
            btn.on_click(self.select_level, level.name)

            self.level_options.append(btn)

    def select_level(self, name):
        LevelManager.instance.set(name)
        game.start()

    def draw(self):
        with reset_matrix():
            self.title.draw()
            self.quit.draw()
            self.level_batch.draw()

    def event(self, _type, *args, **kwargs):

        if _type == EventType.RESIZE:
            w, h = args

            self.title.x = w/2
            self.title.y = h*.9

            self.quit.x = self.quit.content_width
            self.quit.y = self.quit.content_height

            for idx, txt in enumerate(self.level_options):
                txt.x = window.width/4
                txt.y = (window.height*.8)-((idx+1)*txt.content_height)

        self.quit.event(_type, *args, **kwargs)
        for option in self.level_options:
            option.event(_type, *args, **kwargs)


    def update(self, dt):
        pass

class PauseMenu:

    def __init__(self):
        self.title = pg.text.Label("PAUSED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')
        actions = {"Resume":self.resume, "Restart":self.restart, "Mainmenu":self.mainmenu}
        self.options = []
        self.options_batch = pg.graphics.Batch()
        for idx, (act, callback) in enumerate(actions.items()):
            btn = TextButton(act, bold=True, font_size=32,
                anchor_x='center', anchor_y='center',
                batch=self.options_batch)
            btn.x = window.width/2
            btn.y = (window.height*.7) - (idx * btn.content_height)

            btn.hover_color = (255, 0, 0, 255)
            btn.on_click(callback)
            self.options.append(btn)

    def resume(self):
        game.state = GameState.RUNNING

    def restart(self):
        LevelManager.instance.load()
        game.state = GameState.RUNNING

    def mainmenu(self):
        game.state = GameState.MAINMENU

    def reload(self, *args):
        self.title.x = window.width/2
        self.title.y = window.height*.9

        for idx, opt in enumerate(self.options):
            opt.x = window.width/2
            opt.y = (window.height*.7) - (idx * opt.content_height)

    def draw(self):
        with reset_matrix():
            self.title.draw()
            self.options_batch.draw()

    def event(self, _type, *args, **kwargs):
        if _type == EventType.RESIZE:
            w, h = args
            self.reload()

        for opt in self.options:
            opt.event(_type, *args, **kwargs)

    def update(self, dt):
        pass

class InfoPanel:
    MINIMAP_AGENT_SIZE = 25

    def __init__(self, level_name, objs, _map, agents):
        self.level_name = level_name
        self.objectives = objs
        self.map = _map
        self.agents = agents

        self.reload()

        # -- minimap images
        player_img = Resources.instance.sprite("minimap_player")
        image_set_size(player_img, *(self.MINIMAP_AGENT_SIZE,)*2)
        image_set_anchor_center(player_img)
        self.minimap_player = pg.sprite.Sprite(player_img)

        enemy_img = Resources.instance.sprite("minimap_enemy")
        image_set_size(enemy_img, *(self.MINIMAP_AGENT_SIZE,)*2)
        image_set_anchor_center(enemy_img)

        num_enemies = len([a for a in self.agents if isinstance(a, Enemy)])
        self.minimap_enemies = [pg.sprite.Sprite(enemy_img) for _ in range(num_enemies)]

    def reload(self):
        self.panel = self.create_panel()
        self.title = self.create_title()
        self.objs = self.create_objectives()
        self.minimap = self.create_minimap()

    def draw(self):
        with reset_matrix():
            self.panel.blit(0, 0)
            self.title.draw()
            self.objs.draw()
            self.minimap.draw()
            self.draw_minimap_agents()

    def update(self, dt):
        # -- update position of agents on minimap
        w, h = self.minimap.width, self.minimap.height
        offx, offy = self.minimap.x - w, self.minimap.y - h
        sx, sy = [mini/_map for mini, _map in zip((w,h), self.map.size())]

        e_idx = 0
        for agent in self.agents:
            px, py = agent.pos
            _x = offx + (px*sx)
            _y = offy + (py*sy)

            if isinstance(agent, Player):
                self.minimap_player.update(x=_x, y=_y)
            elif isinstance(agent, Enemy):
                self.minimap_enemies[e_idx].update(x=_x, y=_y)
                e_idx += 1

    def event(self, _type, *args, **kwargs):
        if _type == EventType.RESIZE:
            self.reload()

    def create_panel(self):
        w, h = window.get_size()
        img = pg.image.SolidColorImagePattern((100, 100, 100, 200))
        panel_background = img.create_image(w, h)
        return panel_background

    def create_title(self):
        w, h = window.get_size()
        level_name = pg.text.Label(self.level_name.title(), color=(255, 0, 0, 200),
            font_size=24, x=w/2, y=h*.95, anchor_x='center', anchor_y='center', bold=True)
        return level_name

    def create_objectives(self):
        txt_objs = "".join(["- "+obj+'\n' for obj in self.objectives])
        text = f"""Objectives:\n {txt_objs}"""
        w, h = window.get_size()

        return pg.text.Label(text, color=(255, 255, 255, 200), width=w/3,
            font_size=16, x=15, y=h*.9, anchor_y='top', multiline=True, italic=True)

    def create_minimap(self):
        w, h = window.get_size()

        msx, msy = w*.75, h*.9
        minimap = self.map.make_minimap((msx, msy), (255, 255, 255, 150))
        minimap.image.anchor_x = minimap.image.width
        minimap.image.anchor_y = minimap.image.height
        minimap.x = w
        minimap.y = h*.9
        return minimap

    def draw_minimap_agents(self):
        e_idx = 0
        for agent in self.agents:
            if isinstance(agent, Player):
                self.minimap_player.draw()
            elif isinstance(agent, Enemy):
                self.minimap_enemies[e_idx].draw()
                e_idx += 1


class TextInput:

    def __init__(self, text, x, y, width):
        self.batch = pg.graphics.Batch()

        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), dict(color=(0, 0, 0, 255)))
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=self.batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.add_background(x - pad, y - pad,
                            x + width + pad, y + height + pad)

        self.text_cursor = window.get_system_mouse_cursor('text')
        self.set_focus()

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

    def add_background(self, x1, y1, x2, y2):
        vert_list = self.batch.add(4, pyglet.gl.GL_QUADS, None,
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

    def __init__(self, image):
        Button.__init__(self)

    def hover(self, x, y):
        return False

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
def reset_matrix():
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

def distance_sqr(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx**2 + dy**2

def add_wall(space, pos, size):
    shape = pm.Poly.create_box(space.static_body, size=size)
    shape.collision_type = COLLISION_MAP.get("WallType")
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

def get_current_level():
    return LevelManager.instance.current


'''
============================================================
---   MAIN
============================================================
'''

