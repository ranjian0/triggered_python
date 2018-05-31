#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  2048.py
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

import os
import sys
import pickle
import random
import pygame as pg
import itertools as it
from pathlib import Path
from pprint import pprint
from pygame.math import Vector2 as vec2


CAPTION     = '2048'
SIZE        = 500, 600
BOARD_SIZE  = 400, 400

colors = {
    2   : pg.Color("red"),
    4   : pg.Color("blue"),
    8   : pg.Color("yellow"),
    16  : pg.Color("green"),
    32  : pg.Color("violet"),
    64  : pg.Color("purple"),
    128 : pg.Color("magenta"),
    256 : pg.Color("orange"),
    512 : pg.Color("tomato"),
    1024: pg.Color("brown"),
    2048: pg.Color("cyan"),
    4096: pg.Color("lavender")
}

chain = it.chain.from_iterable

def draw_title(surface):
    font_name   = pg.font.match_font('arial')
    font        = pg.font.Font(font_name, 40)

    tsurface    = font.render(CAPTION, True, pg.Color('white'))
    text_rect   = tsurface.get_rect()
    text_rect.midtop = (250, 10)

    surface.blit(tsurface, text_rect)
    pg.draw.line(surface, pg.Color("white"), (0, 100), (500, 100), 3)

def draw_score(surface, score):
    fname   = pg.font.match_font('arial')

    ifont   = pg.font.Font(fname, 20)
    sfont   = pg.font.Font(fname, 10)

    itsurface    = ifont.render(str(score), True, pg.Color('white'))
    stsurface    = sfont.render("Score", True, pg.Color('white'))

    itrect   = itsurface.get_rect(topright=(490, 20))
    strect   = stsurface.get_rect(topright=(490, 10))

    bgrect = pg.Rect(0, 0, 70, 25)
    bgrect.topright = (490, 20)
    pg.draw.rect(surface, pg.Color('gray'), bgrect)
    surface.blit(itsurface, itrect)
    surface.blit(stsurface, strect)

def draw_highscore(surface, hscore=0):
    font_name   = pg.font.match_font('arial')

    ifont   = pg.font.Font(font_name, 20)
    sfont   = pg.font.Font(font_name, 10)

    itsurface    = ifont.render(str(hscore), True, pg.Color('white'))
    stsurface    = sfont.render("High Score", True, pg.Color('white'))

    itrect   = itsurface.get_rect(topright=(490, 62))
    strect   = stsurface.get_rect(topright=(490, 50))

    bgrect = pg.Rect(0, 0, 70, 25)
    bgrect.topright = (490, 62)
    pg.draw.rect(surface, pg.Color('gray'), bgrect)
    surface.blit(itsurface, itrect)
    surface.blit(stsurface, strect)

def load_highscore():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(cur_dir, '2048.data')
    if Path(data_file).exists():
        return pickle.load(open(data_file, 'rb'))['highscore']
    else:
        return 0

def set_highscore(score):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(cur_dir, '2048.data')

    if Path(data_file).exists():
        data = pickle.load(open(data_file, 'rb'))
        if data['highscore'] < score:
            with open(data_file, 'wb') as file:
                pickle.dump({'highscore' : score}, file)
    else:
        with open(data_file, 'wb') as file:
            pickle.dump({'highscore' : score}, file)

class Tile:
    """Tile methods and properties"""

    def __init__(self, value, size, position):
        """Initialize a tile object"""
        self.value = value
        self.size = size
        self.pos = position

        font_name   = pg.font.match_font('arial')
        self.font   = pg.font.Font(font_name, 40)

        self.move_target = None
        self.move_speed = 500

    def draw(self, surface):
        """Draw tile object"""

        sx, sy = self.size
        px, py = self.pos
        r = pg.Rect(px, py, sx, sy)

        pg.draw.rect(surface, colors[self.value], r)

        # Draw Text
        if self.value > 0:
            tsurface    = self.font.render(str(self.value), True, pg.Color('white'))
            text_rect   = tsurface.get_rect(center = r.center)
            surface.blit(tsurface, text_rect)

class Board:
    """Board methods and properties"""

    def __init__(self, size):
        """Initalize the board object"""
        self.size = size

        self.background = self.make_board_background()
        self.tiles      = self.init_tiles()
        self.positions  = self.init_positions()
        self.direction  = (0, 0)
        self.score      = 0
        self.full       = False
        self.movedone   = False
        self.prev_pos   = []

        self.add_tile(3)

    def set_direction(self, d):
        self.direction = d

    def set_tile(self, tile, pos):
        idx, idy = [(x, y) for y, row in enumerate(self.positions)
                            for x, p in enumerate(row) if p == pos][-1]
        self.tiles[idy][idx] = tile

    def make_board_background(self):
        """Create the background for the board"""
        s = pg.Surface(BOARD_SIZE).convert_alpha()
        s.fill(pg.Color("grey"))

        w = 5
        cx, cy = self.size
        sx, sy = [s/c for s, c in zip(BOARD_SIZE, self.size)]
        for x in range(cx):
            for y in range(cy):
                pg.draw.rect(s, pg.Color("white"), [x*sx, y*sy, sx, sy], w)
        return s

    def init_tiles(self):
        """Initialize tiles for the board"""
        sx, sy = self.size
        return [[None for _ in range(sx)] for _ in range(sy)]

    def init_positions(self):
        cx, cy = self.size
        sx, sy = [int(s/c) for s, c in zip(BOARD_SIZE, self.size)]
        offx, offy = 55, 155

        return [[(offx + x*sx, offy + y*sy) for x in range(cx)]
                                            for y in range(cy)]

    def add_tile(self, count=1):
        """Add count number of tiles to the board"""
        sx, sy = self.size
        tx, ty = [s/c - 10 for s, c in zip(BOARD_SIZE, self.size)]

        empty_positions = list(set(chain(self.positions)) - set(t.pos for t in chain(self.tiles) if t))

        for _ in range(count):
            # create new tile
            random.seed(pg.time.get_ticks())
            p = random.choice(empty_positions)
            v = 2
            if len(empty_positions) < len(list(chain(self.tiles))):
                v = 2 if max(list([t.value for t in chain(self.tiles) if t])) < 1024 else random.choice([2, 4])
            t = Tile(v, (tx, ty), p)

            # add to board
            self.set_tile(t, p)

            # remove p from empty_positions
            empty_positions.remove(p)

    def draw(self, screen):
        """Draw the board"""
        # -- background
        screen.blit(self.background, self.background.get_rect(topleft=(50, 150)))

        # -- tiles
        for tile in [t for row in self.tiles for t in row if t]:
            tile.draw(screen)

    def update(self, dt):
        """Update tiles"""
        if all(list(chain(self.tiles))):
            self.full = True

        if not any(self.direction):
            return

        tiles = [(x, y, t) for y, row in enumerate(self.tiles)
                           for x, t   in enumerate(row) if t]

        current_positions = [(t[0], t[1]) for t in tiles]

        if self.direction[0]:
            tiles.sort(key=lambda t: t[2].pos[0], reverse=True if self.direction[0] > 0 else False)
        if self.direction[1]:
            tiles.sort(key=lambda t: t[2].pos[1], reverse=True if self.direction[1] > 0 else False)

        moving = []
        for idx, idy, tile in tiles:

            # -- Calculate next position on board based on direction
            tx, ty = tile.pos
            dx, dy = self.direction
            sx, sy = [int(s/c) for s, c in zip(BOARD_SIZE, self.size)]
            npos   = tx+(dx * sx), ty+(dy * sy)

            # -- Determine some flags for calculated next position
            in_board    = npos in [p for row in self.positions for p in row]
            occupied    = npos in [t.pos for row in self.tiles for t in row if t]
            empty       = npos not in [t.pos for row in self.tiles for t in row if t]

            # -- if npos is empty, move there
            if in_board and empty:
                tile.pos = npos

                # change board position
                self.tiles[idy][idx] = None
                self.tiles[idy + dy][idx + dx] = tile

            # -- if npos has tile with same value as tile
            if occupied:
                ntile = self.tiles[idy + dy][idx + dx]

                if tile != ntile and tile.value == ntile.value:
                    self.tiles[idy][idx] = None
                    ntile.value *= 2

                    # Add score
                    self.score += ntile.value
                    # pg.time.wait(50)

        updated_positions = [(x, y) for y, row in enumerate(self.tiles)
                                    for x, t   in enumerate(row) if t]
        no_merge = len(current_positions) == len(updated_positions)
        no_move = current_positions == updated_positions
        if no_move and no_merge:
            self.movedone = True

        if self.movedone:
            end = [(x, y) for y, r in enumerate(self.tiles)
                            for x, t in enumerate(r) if t]

            if end != self.prev_pos:
                self.add_tile()
            self.movedone = False
            self.direction = (0, 0)
            self.prev_pos = [(x, y) for y, r in enumerate(self.tiles)
                                    for x, t in enumerate(r) if t]

action_map = [
    {"keys" : [pg.K_w, pg.K_UP],    "direction":( 0, -1)},
    {"keys" : [pg.K_s, pg.K_DOWN],  "direction":( 0,  1)},
    {"keys" : [pg.K_a, pg.K_LEFT],  "direction":(-1,  0)},
    {"keys" : [pg.K_d, pg.K_RIGHT], "direction":( 1,  0)},
]

def main():
    pg.init()
    pg.display.set_caption(CAPTION)
    screen  = pg.display.set_mode(SIZE, 0, 32)
    clock   = pg.time.Clock()

    # Objects
    board = Board((4, 4))
    hscore = load_highscore()

    dt      = 0
    while True:
        # Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()

                for action in action_map:
                    if event.key in action.get("keys"):
                        board.set_direction(action.get("direction"))

        # Draw
        screen.fill((100, 100, 100))

        draw_title(screen)
        draw_score(screen, board.score)
        draw_highscore(screen, hscore)
        board.draw(screen)

        pg.display.flip()

        # Update
        dt = clock.tick(20) / 1000.0
        board.update(dt)
        hscore = max(hscore, board.score)

        if board.full:
            set_highscore(hscore)
            break

if __name__ == '__main__':
    main()
