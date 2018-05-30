#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  2048.py

import sys
import pygame as pg
import random as rnd
from copy import copy
from pprint import pprint


colors = {
    0   : pg.Color("grey"),
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

def make_board(sx=5, sy=5):
    """
    Create a list of lists to represent the board
    """
    return [[0 for x in range(sx)] for y in range(sy)]

def initialize_board(b):
    """
    Add some default values to an empty board
    """

    for _ in range(3):

        idx = rnd.randint(0, len(b[0])-1)
        idy = rnd.randint(0, len(b)-1)

        b[idy][idx] = 2

def add_value(b):
    """
    Add some a value to the board
    """

    # Ensure that the board is not full
    assert len([val for row in b for val in row if val==0]) > 0

    # Procede to add a value
    idx = rnd.randint(0, len(b[0])-1)
    idy = rnd.randint(0, len(b)-1)
    option = b[idy][idx]

    while  option != 0:
        idx = rnd.randint(0, len(b[0])-1)
        idy = rnd.randint(0, len(b)-1)
        option = b[idy][idx]

    b[idy][idx] = rnd.choice([2, 4])

def columns(b):
    cols = []
    for i in range(len(b[0])):
        cols.append([row[i] for row in b])
    return cols

def board_from_columns(cols):
    res = []
    for i in range(len(cols)):
        row = []
        for col in cols:
            row.append(col[i])
        res.append(row)
    return res

def move_values(b, direction):

    dx, dy = direction
    tmp_board = copy(b)
    if dx:
        # Move left/right
        for idy, row in enumerate(tmp_board):
            # Normalize row
            nrow = row if dx < 1 else list(reversed(row))
            # Valid and null items
            items = [item for item in nrow if item]
            nulls = [0 for _ in range(len(nrow) - len(items))]
            # Merge result and apply
            res = nulls + list(reversed(items)) if dx==1 else items + nulls
            b[idy] = res

    if dy:
        # Move up/down
        result = []
        for idx, col in enumerate(columns(tmp_board)):
            # Normalize columns
            ncol = col if dy == 1 else list(reversed(col))
            # Valid and null items
            items = [item for item in ncol if item]
            nulls = [0 for _ in range(len(ncol) - len(items))]
            # Merge result and apply
            res = items + nulls if dy==1 else nulls + list(reversed(items))
            result.append(res)

        for idy, row in enumerate(board_from_columns(result)):
            b[idy] = row

def merge(b, direction):

    dx, dy = direction

    if dx:
        move_values(b, direction)

        for idy, row in enumerate(copy(b)):
            # Normalize row
            nrow = row if dx < 1 else list(reversed(row))

            # Merge pairs
            lmax = len(nrow)-1
            for i in range(0, lmax, 1):
                p1, p2 = nrow[i], nrow[i+1]
                if p1 == p2 and p1 != 0:
                    if dx == 1:
                        b[idy][lmax-i] = p1 + p2
                        b[idy][lmax-(i+1)] = 0
                    else:
                        b[idy][i] = p1 + p2
                        b[idy][i+1] = 0

        move_values(b, direction)

    if dy:
        move_values(b, direction)

        tmp = copy(b)
        for idx, col in enumerate(columns(tmp)):
            # Normalize columns
            ncol = col if dy == 1 else list(reversed(col))

            # Merge pairs
            lmax = len(ncol)-1
            for i in range(0, lmax, 1):
                p1, p2 = ncol[i], ncol[i+1]
                if p1 == p2 and p1 != 0:
                    if dy == 1:
                        b[i][idx] = p1 +p2
                        b[i+1][idx] = 0
                    else:
                        b[lmax-i][idx] = p1 +p2
                        b[lmax-(i+1)][idx] = 0

        move_values(b, direction)

def draw_board(b, surface):

    width, height = pg.display.get_surface().get_size()
    font = pg.font.Font(None, 48)

    border = 10
    tsx = (width - (border * (len(b[0])+1))) / len(b[0])
    tsy = (height - (border * (len(b)+1))) / len(b)

    for y in range(len(b)):
        for x in range(len(b[0])):
            top = border + (y*(tsy+border))
            left = border + (x*(tsx+border))
            rect = pg.draw.rect(surface, colors[b[y][x]], [left, top, tsx, tsy])

            # text
            if b[y][x]:
                txt = font.render(str(b[y][x]), 0, pg.Color("white"))
                surface.blit(txt, txt.get_rect(center = rect.center))

def main(args):
    pg.init()
    pg.display.set_caption("2048")
    screen = pg.display.set_mode((500, 500), 0, 32)
    clock = pg.time.Clock()

    # Board initialization
    board = make_board()
    initialize_board(board)

    current, previous = copy(board), copy(board)
    dt = 0
    while True:

        # Events
        for ev in pg.event.get():

            if ev.type == pg.QUIT:
                sys.exit(0)

            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_ESCAPE:
                    sys.exit(0)

                if ev.key == pg.K_w or ev.key == pg.K_UP:
                    merge(board, (0, 1))
                if ev.key == pg.K_s or ev.key == pg.K_DOWN:
                    merge(board, (0, -1))
                if ev.key == pg.K_a or ev.key == pg.K_LEFT:
                    merge(board, (-1, 0))
                if ev.key == pg.K_d or ev.key == pg.K_RIGHT:
                    merge(board, (1, 0))

                current = copy(board)

        # Draw
        screen.fill((100, 100, 100))

        draw_board(board, screen)

        pg.display.flip()

        # Update
        dt = clock.tick(60) / 1000

        if current != previous:
            add_value(board)
            previous = current

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
