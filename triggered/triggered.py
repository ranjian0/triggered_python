#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  triggered.py
#
#  Copyright 2017 Ian Ichung'wah Karanja <karanjaichungwa@gmail.com>
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

import sys
import time
import math
import heapq
import random
import pygame as pg
import pymunk as pm
import itertools as it

from enum          import Enum
from collections   import namedtuple
from pygame.sprite import Sprite, Group
from pygame.math   import Vector2     as vec2
from pymunk        import pygame_util as putils


SIZE        = (800, 600)
CAPTION     = "Triggered"
BACKGROUND  = (100, 100, 100)
TRANSPARENT = (0, 0, 0, 0)
IMPUT_MAP   = {
    pg.K_w : (0, -1),
    pg.K_s : (0, 1),
    pg.K_a : (-1, 0),
    pg.K_d : (1, 0)
}

COLLISION_MAP = {
    "PlayerType" : 1,
    "EnemyType"  : 2,
}

SPACE        = pm.Space()
PHYSICS_STEP = 50
putils.positive_y_is_up = False


def main():
    pg.init()
    pg.display.set_caption(CAPTION)
    screen  = pg.display.set_mode(
        SIZE, pg.RESIZABLE, 32)

    clock   = pg.time.Clock()

    manager = SceneManager()
    manager.add(MainScene, True)
    manager.add(GameScene)
    manager.add(PauseScene)
    manager.add(LevelPassed)
    manager.add(LevelFailed)
    manager.add(GameOver)

    setup_collisions()

    while True:
        # -- events
        for event in pg.event.get():
            manager.event(event)

            if event.type == pg.QUIT:
                sys.exit()

            if event.type == pg.VIDEORESIZE:
                resize(event, screen)

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if isinstance(manager.current, GameScene):
                        manager.switch(PauseScene.NAME)

        # -- draw
        screen.fill(BACKGROUND)
        manager.draw(screen)
        pg.display.flip()

        # -- update
        dt = clock.tick(60) / 1000
        for _ in range(PHYSICS_STEP):
            SPACE.step(0.1 / PHYSICS_STEP)
        manager.update(dt)

def resize(ev, screen):
    screen = pg.display.set_mode(
        ev.size, pg.RESIZABLE, 32)

    # level = LevelManager.instance.get_current()
    # level.MAP.resize()

def add_wall(pos, size):

    shape = pm.Poly.create_box(SPACE.static_body, size=size)
    shape.body.position = pos
    SPACE.add(shape)

def setup_collisions():

    # Player-Enemy Collision
    def player_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        pshape = arbiter.shapes[0]
        eshape  = arbiter.shapes[1]

        normal = pshape.body.position - eshape.body.position
        normal = normal.normalized()
        pshape.body.position = eshape.body.position + (normal * (pshape.radius*2))
        return True

    handler = SPACE.add_collision_handler(
            COLLISION_MAP.get("PlayerType"),
            COLLISION_MAP.get("EnemyType")
        )
    handler.begin = player_enemy_solve

    # Enemy-Enemy Collision
    def enemy_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        eshape  = arbiter.shapes[0]
        eshape1 = arbiter.shapes[1]

        normal = eshape.body.position - eshape1.body.position
        normal = normal.normalized()
        perp   = vec2(normal.y, -normal.x)

        eshape.body.position = eshape.body.position + (perp * (eshape.radius/2))
        return True

    handler = SPACE.add_collision_handler(
            COLLISION_MAP.get("EnemyType"),
            COLLISION_MAP.get("EnemyType")
        )
    handler.begin = enemy_enemy_solve


class Drawable(Sprite):
    def __init__(self, anchor="center", offset=(0,0)):
        super(Drawable, self).__init__()

        self.anchor = anchor
        self.offset = offset
        self.calc_pos(anchor, offset)

    def calc_pos(self, anchor, off):
        # -- calculate relative screen position based on anchor and offset
        display  = pg.display.get_surface()
        rect = display.get_rect().copy()

        self.pos = (0, 0)
        if anchor == 'center':
            px, py = rect.center
            px += off[0]
            py += off[1]
            self.pos = (px, py)

    def draw(self, surface):
        pass

    def update(self, dt):
        pass

    def event(self, event):
        pass

class Label(Drawable):
    """Text rendering widget"""
    def __init__(self, text, position,
                    font_size   = 25,
                    fg          = pg.Color("white"),
                    bg          = None):

        super(Label, self).__init__()
        pg.font.init()

        self.fg   = fg
        self.bg   = bg
        self.pos  = position
        self.text = text
        self.size = font_size

        self.font    = pg.font.Font(None, self.size)
        self.surface = self.font.render(self.text, True, self.fg, self.bg)
        self.rect    = self.surface.get_rect(center=self.pos)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

class Button(Drawable):
    """Button widget"""
    def __init__(self, text, size, position,
                    fg          = pg.Color("white"),
                    bg          = pg.Color("red"),
                    on_clicked  = lambda : print("Button Clicked"),
                    font_size   = 25,
                    hover_color = pg.Color("yellow")):

        super(Button, self).__init__()
        self.text = text
        self.size = size
        self.pos  = position

        self.foreground = fg
        self.background = bg
        self.on_clicked = on_clicked
        self.hover_col  = hover_color

        self.surface = pg.Surface(size)
        self.rect    = self.surface.get_rect(center=self.pos)
        self.label   = Label(self.text, (size[0]/2, size[1]/2), font_size, fg)

        self.state_hovered = False

    def draw(self, surface):

        if self.state_hovered:
            self.surface.fill(self.hover_col)
        else:
            self.surface.fill(self.background)

        self.label.draw(self.surface)
        surface.blit(self.surface, self.rect)

    def update(self, dt):
        mouse = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.state_hovered = True
        else:
            self.state_hovered = False

    def event(self, event):
        if self.state_hovered:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if callable(self.on_clicked):
                    self.on_clicked()

class Timer(Drawable):
    """Timer Widget"""
    def __init__(self, size, position,
                    start_value = 10,
                    fg          = pg.Color("green"),
                    bg          = pg.Color("black"),
                    on_complete = lambda : print("Timer Complete")):

        super(Timer, self).__init__()

        self.size  = size
        self.pos   = position
        self.start = start_value
        self.value = start_value

        self.foreground  = fg
        self.background  = bg
        self.on_complete = on_complete

        self.elapsed     = 0
        self.completed   = False

        self.surface = pg.Surface(self.size)
        self.rect    = self.surface.get_rect(center=self.pos)

    def reset(self):
        self.value = self.start

    def draw(self, surface):
        r = pg.Rect((0, 0), self.size)
        pg.draw.rect(self.surface, self.background, r)

        r = r.inflate(-10, -10)
        r.center = (self.size[0]/2, self.size[1]/2)
        r.width  *= self.value/self.start
        pg.draw.rect(self.surface, self.foreground, r)

        surface.blit(self.surface, self.rect)

    def update(self, dt):
        self.elapsed += dt

        if not self.completed and self.elapsed < self.start:
            self.value = self.start - self.elapsed
        elif not self.completed and self.elapsed >= self.start:
            self.value     = self.start
            if callable(self.on_complete):
                self.on_complete()

class Map(Drawable):

    def __init__(self, data,
                    fg        = pg.Color(77,77,77),
                    bg        = pg.Color(120, 95, 50),
                    node_size = 100):

        super(Map, self).__init__()
        self.data       = data
        self.entities   = []
        self.node_size  = node_size
        self.foreground = fg
        self.background = bg

        self.walls      = []
        self.surface    = self.make_map()
        self.rect       = self.surface.get_rect(topleft=(1, 1))

        display  = pg.display.get_surface()
        self.viewport = display.get_rect().copy()

        self.pathfinder = PathFinder(data, node_size)
        self.spawn_data = self.parse_spawn_points()

    def add(self, ent):
        self.entities.append(ent)

    def remove(self, ent):
        self.entities.remove(ent)

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
                    add_wall(r.center, (nsx/2, nsy/2))

                    # Fill gaps
                    # -- gaps along x-axis
                    if x < len(row) - 1 and self.data[y][x + 1] == "#":
                        r = pg.draw.rect(surf, self.foreground, [offx + nsx/2, offy, nsx/2, nsy/2])
                        pg.draw.rect(surf, wall_edge_col, [offx + nsx/2, offy, nsx/2, nsy/2], wall_edge_thk)
                        self.walls.append(r)
                        add_wall(r.center, (nsx/2, nsy/2))


                    # -- gaps along y-axis
                    if y < len(self.data) - 1 and self.data[y + 1][x] == "#":
                        r = pg.draw.rect(surf, self.foreground, [offx, offy + nsy/2, nsx/2, nsy/2])
                        pg.draw.rect(surf, wall_edge_col, [offx, offy + nsy/2, nsx/2, nsy/2], wall_edge_thk)
                        self.walls.append(r)
                        add_wall(r.center, (nsx/2, nsy/2))

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

    def draw(self, surface):
        new_img = self.surface.copy()

        options = putils.DrawOptions(new_img)
        SPACE.debug_draw(options)

        for ent in self.entities:
            ent.draw(new_img)

        surface.blit(new_img, (0, 0), self.viewport)

    def update(self, dt):
        for ent in self.entities:
            ent.update(dt)

        player = [ent for ent in self.entities if isinstance(ent, Player)][-1]

        display  = pg.display.get_surface()
        self.viewport = display.get_rect().copy()

        self.viewport.center = player.rect.center
        self.viewport.clamp_ip(self.rect)
        player.viewport = self.viewport

        # Clamp player to map
        player.rect.clamp_ip(self.rect)

    def event(self, ev):
        for ent in self.entities:
            ent.event(ev)

class Bullet(Drawable):

    def __init__(self, pos, angle,
            color=pg.Color('black')):
        Sprite.__init__(self)

        size = (5, 5)
        self.color = color
        self.image = self.make_image(size)
        self.rect = self.image.get_rect(center=pos)

        self.true_pos = list(self.rect.center)
        self.angle = -math.radians(angle - 90)
        self.speed = 5

    def make_image(self, size):
        img = pg.Surface(size).convert_alpha()
        img.fill(TRANSPARENT)
        rect = img.get_rect()

        pg.draw.rect(img, self.color, [0, 0, size[0], size[1]])

        return img

    def update(self, dt):
        self.true_pos[0] += math.cos(self.angle) * self.speed
        self.true_pos[1] += math.sin(self.angle) * self.speed

        self.rect.topleft = self.true_pos

        self.collide_map()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def collide_map(self):
        walls = LevelManager.instance.get_current().MAP.walls
        for wall in walls:
            if self.rect.colliderect(wall):
                self.kill()

class Player(Drawable):

    def __init__(self, position, size):
        super(Player, self).__init__()

        self.pos    = position
        self.size   = size
        self.turret = None

        # Create Player Image
        self.original_img = self.make_image(size)
        self.surface      = self.original_img.copy()
        self.rect         = self.surface.get_rect(center=position)

        # Player Variables
        self.angle    = 0
        self.speed    = 150
        self.direction = (0, 0)
        self.bullets   = Group()
        self.rotate(pg.mouse.get_pos())

        self.ammo    = 50
        self.health  = 100
        self.damage  = 10

        self.body = pm.Body(1, 100)
        self.body.position = self.rect.center
        self.shape = pm.Circle(self.body, size[0]/2)
        self.shape.collision_type = COLLISION_MAP.get("PlayerType")
        SPACE.add(self.body, self.shape)

        display  = pg.display.get_surface()
        self.viewport = display.get_rect().copy()

    def make_image(self, size):
        img = pg.Surface(size).convert_alpha()
        img.fill(TRANSPARENT)

        rect = img.get_rect()

        self.turret = pg.draw.rect(img, pg.Color('black'), [rect.center[0] - 5, 25, 10, 50])
        pg.draw.ellipse(img, pg.Color('black'), rect.inflate(-10, -10))
        pg.draw.ellipse(img, pg.Color('tomato'), rect.inflate(-20, -20))

        return img

    def rotate(self, pos):
        offset = (pos[1] - self.rect.centery, pos[0] - self.rect.centerx)
        self.angle = 90 - math.degrees(math.atan2(*offset))

        self.surface = pg.transform.rotate(self.original_img, self.angle)
        self.rect = self.surface.get_rect(center=self.rect.center)

    def shoot(self):
        if self.ammo <= 0:
            return
        self.ammo -= 1

        pos = pg.mouse.get_pos()
        px, py, *_ = self.viewport
        pos = pos[0] + px, pos[1] + py

        vec = vec2(pos[0] - self.rect.centerx, pos[1] - self.rect.centery).normalize()
        gun_pos = vec2(self.rect.center) + (vec * vec2(self.turret.center).length()/2)
        self.bullets.add(Bullet(gun_pos, self.angle))

    def check_health(self):
        if self.health <= 0:
            SceneManager.instance.switch(LevelFailed.NAME)
            # self.kill()
            # _map = LevelManager.instance.get_current().MAP
            # _map.remove(self)

    def hit(self):
        """ Called when enemy bullet hits us (see Enemy Class)"""
        self.health -= self.damage

    def draw_ammo(self, surface):
        """ Draw ammo on top-right corner of screen"""
        # - draw one clip for every ten bullets
        rect = surface.get_rect()
        for i in range(self.ammo // 10):
            pg.draw.rect(surface, pg.Color("yellow"),
                    [500 + (i*15), 5, 10, 25]
                )

    def draw(self, surface):
        surface.blit(self.surface, self.rect)
        self.bullets.draw(surface)
        # self.draw_ammo(surface)

    def event(self, event):
        if not isinstance(SceneManager.instance.current, GameScene): return
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.shoot()

    def update(self, dt):
        self.bullets.update(dt)

        # Keys and mouse
        pos = pg.mouse.get_pos()
        keys = pg.key.get_pressed()

        # -- Rotate
        px, py, *_ = self.viewport
        pos = pos[0] + px, pos[1] + py
        vec = vec2(pos[0] - self.rect.centerx, pos[1] - self.rect.centery)
        if vec.length() > 5:
            self.rotate(pos)
            pass

        # -- Move
        dx, dy = 0, 0
        for key, _dir in IMPUT_MAP.items():
            if keys[key]:
                dx, dy = _dir

        # -- running
        speed = self.speed
        if keys[pg.K_RSHIFT] or keys[pg.K_LSHIFT]:
            speed *= 1.5

        bx, by = self.body.position
        bx += dx * speed * dt
        by += dy * speed * dt

        self.body.position = (bx, by)
        self.rect.center = (bx, by)

        self.check_health()

class EnemyState(Enum):
    IDLE    = 0
    PATROL  = 1
    CHASE   = 2
    ATTACK  = 3

class Enemy(Drawable):

    def __init__(self, position, size,
                    waypoints=None):
        super(Enemy, self).__init__()

        self.pos   = position
        self.size  = size
        self.state = EnemyState.IDLE
        self.speed = 75
        self.turret = None

        self.original_img = self.make_image()
        self.surface      = self.original_img.copy()
        self.rect         = self.surface.get_rect(center=position)

        self.waypoints = it.cycle(waypoints)
        self.target    = next(self.waypoints)

        self.patrol_epsilon = 2
        self.chase_radius   = 300
        self.attack_radius  = 100

        self.attack_frequency = 50
        self.current_attack   = 0

        self.angle   = 0
        self.bullets = Group()

        self.health  = 100
        self.damage  = 15

        self.body = pm.Body(1, 100)
        self.body.position = self.rect.center
        self.shape = pm.Circle(self.body, size[0]/2)
        self.shape.collision_type = COLLISION_MAP.get("EnemyType")
        SPACE.add(self.body, self.shape)


    def make_image(self):
        img = pg.Surface(self.size).convert_alpha()
        img.fill(TRANSPARENT)

        rect = img.get_rect()
        center = rect.center

        self.turret = pg.draw.rect(img, pg.Color('black'), [center[0] - 5, 40, 10, 40])
        pg.draw.ellipse(img, pg.Color('black'), rect.inflate(-10, -10))
        pg.draw.ellipse(img, pg.Color('green'), rect.inflate(-20, -20))
        return img

    def draw(self, surface):
        surface.blit(self.surface, self.rect)
        self.bullets.draw(surface)

    def update(self, dt):
        player = LevelManager.instance.get_current().get_player()
        player_distance = (vec2(self.rect.center) - vec2(player.rect.center)).length_squared()

        # if player_distance < self.chase_radius**2:
        #     self.state = EnemyState.CHASE
        # else:
        #     self.state = EnemyState.PATROL

        # if player_distance < self.attack_radius**2:
        #     self.state = EnemyState.ATTACK

        if self.state == EnemyState.IDLE:
            self.state = EnemyState.PATROL
        elif self.state == EnemyState.PATROL:
            self.patrol(dt)
        elif self.state == EnemyState.CHASE:
            self.chase(player.rect.center, dt)
            pass
        elif self.state == EnemyState.ATTACK:
            self.attack(player.rect.center)

        self.bullets.update(dt)
        bx, by = self.body.position
        self.rect.center = (bx, by)

        self.check_shot_at(player)
        if self.health <= 0:
            self.kill()
            _map = LevelManager.instance.get_current().MAP
            _map.remove(self)


    def patrol(self, dt):
        diff     = vec2(self.rect.center) - vec2(self.target)
        distance = diff.length_squared()
        if distance < self.patrol_epsilon:
            self.target = next(self.waypoints)

        self.look_at(self.target)
        self.move_to_target(self.target, dt)

    def chase(self, player_pos, dt):
        self.look_at(player_pos)
        self.move_to_target(player_pos, dt)

    def attack(self, player):
        self.look_at(player)
        self.current_attack += 1

        if self.current_attack == self.attack_frequency:
            vec = vec2(player[0] - self.rect.centerx, player[1] - self.rect.centery).normalize()
            gun_pos = vec2(self.rect.center) + (vec * vec2(self.turret.center).length()/2)
            self.bullets.add(Bullet(gun_pos, self.angle))

            self.current_attack = 0

    def move_to_target(self, target, dt):
        diff      = vec2(target) - vec2(self.rect.center)
        if diff.length_squared():
            dx, dy = diff.normalize()

            bx, by = self.body.position
            bx += dx * self.speed * dt
            by += dy * self.speed * dt
            self.body.position = (bx, by)

    def look_at(self, target):
        offset = (target[1] - self.rect.centery, target[0] - self.rect.centerx)
        self.angle  = 90 - math.degrees(math.atan2(*offset))

        self.surface = pg.transform.rotate(self.original_img, self.angle)
        self.rect    = self.surface.get_rect(center=self.rect.center)

    def check_shot_at(self, player):

        # Check if player bullets hit us
        for bullet in player.bullets:
            if self.rect.colliderect(bullet.rect):
                self.health -= self.damage
                bullet.kill()

        # Check if our bullets hit the player
        for bullet in self.bullets:
            if player.rect.colliderect(bullet.rect):
                player.hit()
                bullet.kill()


class Level(Drawable):
    NAME    = "Level"
    MAP     = None
    PLAYER  = None
    ENEMIES = []
    TIMER   = None
    COLLECTIBLES = []

    def __init__(self):
        super(Level, self).__init__()

        self.MAP.add(self.PLAYER)
        for en in self.ENEMIES:
            self.MAP.add(en)

        if self.COLLECTIBLES:
            for col in self.COLLECTIBLES:
                self.MAP.add(col)

    def check_complete(self):
        if not self.ENEMIES:
            SceneManager.instance.switch(LevelPassed.NAME)
        else:
            SceneManager.instance.switch(LevelFailed.NAME)

    def get_player(self):
        return self.PLAYER

    def draw(self, surface):
        self.MAP.draw(surface)
        self.TIMER.draw(surface)

    def update(self, dt):
        self.MAP.update(dt)
        self.TIMER.update(dt)

    def event(self, ev):
        self.MAP.event(ev)

class LevelManager:

    instance = None
    def __init__(self, levels):
        LevelManager.instance = self

        self.levels     = levels
        self.current    = 0

    def get_current(self):
        return self.levels[self.current]

    def go_next(self):
        if self.current < len(self.levels)-1:
            self.current += 1
            SceneManager.instance.switch(GameScene.NAME)
        else:
            # Reinstanciate all levels, incase player goes again
            types = [type(level) for level in self.levels]
            self.levels.clear()
            self.levels  = [typ() for typ in types]
            self.current = 0

            SceneManager.instance.switch(GameOver.NAME)

class LevelOne(Level):
    NAME    = "Kill Them All"

    def __init__(self):


        self.MAP     = Map(
        [['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
         ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
         ['#', ' ', '#', '#', '#', '#', '#', ' ', '#', ' ', '#'],
         ['#', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#', ' ', '#'],
         ['#', ' ', '#', '#', '#', '#', '#', 'e', '#', 'e', '#'],
         ['#', 'e', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#'],
         ['#', ' ', '#', 'e', '#', '#', '#', '#', '#', ' ', '#'],
         ['#', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#'],
         ['#', ' ', '#', '#', '#', '#', '#', '#', '#', ' ', '#'],
         ['#', 'p', ' ', 'e', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
         ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']]
         )

        self.TIMER    = Timer((150, 30), (80, 20), 500,
            on_complete=lambda : LevelManager.instance.get_current().check_complete())

        data = self.MAP.spawn_data
        self.PLAYER   = Player(data.get('player_position'), (50, 50))
        self.ENEMIES  = []
        for point in data['enemy_position']:
            patrol_points = random.sample(data['patrol_positions'],
                random.randint(2, len(data['patrol_positions'])//2))

            patrol = self.MAP.pathfinder.calc_patrol_path([point] + patrol_points)
            e = Enemy(point, (40, 40), patrol)
            self.ENEMIES.append(e)

        super(LevelOne, self).__init__()


class Scene(object):
    NAME      = "Scene"
    DRAWABLES = []

    def __init__(self):
        assert self.NAME != "Scene", "Scene must have unique name"
        print("Initialized : ", self)

    def draw(self, surface):
        for drawable in self.DRAWABLES:
            if isinstance(drawable, Drawable):
                drawable.draw(surface)

    def update(self, dt):
        for drawable in self.DRAWABLES:
            if isinstance(drawable, Drawable):
                drawable.update(dt)

    def event(self, ev):
        for drawable in self.DRAWABLES:
            if isinstance(drawable, Drawable):
                drawable.event(ev)

class SceneManager:

    instance = None
    def __init__(self):
        SceneManager.instance = self

        self.scenes      = []
        self.start_scene = None
        self.current     = None

    def add(self, scene, is_main=False):
        if is_main:
            self.start_scene = scene()
            self.current     = scene()
        self.scenes.append(scene)

    def switch(self, name):
        self.current = [scn for scn in self.scenes
                        if scn.NAME == name][-1]()

    def draw(self, surface):
        if self.current:
            self.current.draw(surface)

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def event(self, ev):
        if self.current:
            self.current.event(ev)

class MainScene(Scene):
    NAME = "MainMenu"

    def __init__(self):
        Scene.__init__(self)
        self.DRAWABLES = [
            Label("TRIGGERED", (400, 50), font_size=60, fg=pg.Color("Red")),

            Button("PLAY", (200, 50), (400, 200), font_size=40,
                    on_clicked=lambda : SceneManager.instance.switch(GameScene.NAME)),

            Button("EXIT", (200, 50), (400, 270), font_size=40,
                    on_clicked=lambda : sys.exit()),

            Label("Created by Ian Karanja", (700, 580), font_size=20, fg=pg.Color("White")),
        ]

class GameScene(Scene):
    NAME = "GAME"

    def __init__(self):
        self.levels = LevelManager([
                        LevelOne()
                    ])

    def draw(self, surface):
        super().draw(surface)
        self.levels.get_current().draw(surface)

    def update(self, dt):
        super().update(dt)
        self.levels.get_current().update(dt)

    def event(self, event):
        super().event(event)
        self.levels.get_current().event(event)

class PauseScene(Scene):
    NAME = "Pause"

    def __init__(self):
        Scene.__init__(self)
        self.DRAWABLES = [
            Label("PAUSED", (400, 300), font_size=60, fg=pg.Color("Red")),

            Button("RESUME", (200, 50), (650, 550), font_size=40,
                    on_clicked=lambda : SceneManager.instance.switch(GameScene.NAME)),

            Button("QUIT", (200, 50), (150, 550), font_size=40,
                    on_clicked=lambda : SceneManager.instance.switch(MainScene.NAME)),
        ]

class LevelFailed(Scene):
    NAME = "LevelFailed"

    def __init__(self):
        Scene.__init__(self)
        self.DRAWABLES = [
            Label("LEVEL FAILED", (400, 300), font_size=60, fg=pg.Color("Red")),

            Button("RETRY", (200, 50), (650, 550), font_size=40,
                    on_clicked=lambda : SceneManager.instance.switch(GameScene.NAME)),

            Button("QUIT", (200, 50), (150, 550), font_size=40,
                    on_clicked=lambda : SceneManager.instance.switch(MainScene.NAME)),
        ]

class LevelPassed(Scene):
    NAME = "LevelPassed"

    def __init__(self):
        Scene.__init__(self)
        self.DRAWABLES = [
            Label("LEVEL PASSED", (400, 300), font_size=60, fg=pg.Color("Red")),

            Button("NEXT", (200, 50), (650, 550), font_size=40,
                    on_clicked=lambda : LevelManager.instance.go_next()),

            Button("QUIT", (200, 50), (150, 550), font_size=40,
                    on_clicked=lambda : SceneManager.instance.switch(MainScene.NAME)),
        ]

class GameOver(Scene):
    NAME = "GameOver"

    def __init__(self):
        Scene.__init__(self)
        self.DRAWABLES = [
            Label("GAME OVER", (400, 300), font_size=60, fg=pg.Color("Red")),

            Button("QUIT", (200, 50), (150, 550), font_size=40,
                    on_clicked=lambda : SceneManager.instance.switch(MainScene.NAME)),
        ]


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
    path.append(start) # optional
    path.reverse() # optional
    return path

if __name__ == '__main__':
    main()
