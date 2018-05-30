#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  snake.py
#
#  Copyright 2017 Ian Ichung'wah Karanja <karanjaichungwa@gmail.com>


import sys
import random
import pygame as pg
from pygame.math import Vector2 as vec2

# GLOBALS
FPS         = 5
SIZE        = 500, 500
CAPTION     = "Snake"
BACKGROUND  = 100, 100, 100


GS          = 25
keys        = [pg.K_w, pg.K_s, pg.K_a, pg.K_d]
opt_keys    = [pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT]
directions  = [(0, -1), (0, 1), (-1, 0), (1, 0)]


class Snake:
    """ Make definitions for snake properties and behaviour"""

    def __init__(self, pos, segments, color):
        """Initialize the snake object"""

        self.pos = pos
        self.segments = segments
        self.color = color
        self.size = 25

        self.snake = self.make_snake()
        self.direction = (0, -1)

    def make_snake(self):
        """Create the segments of the snake"""

        segs = []
        px, py = self.pos
        s = self.size
        for i in range(self.segments):
            r = pg.Rect(px, py+(i*s), s, s)
            segs.append(r)
        return segs

    def draw(self, surface):
        """Iterate over all snake segments and draw"""

        for seg in self.snake:
            pg.draw.rect(surface, self.color, seg)
            pg.draw.rect(surface, pg.Color('black'), seg, 3)

    def event(self, ev):
        """Handle all events accepted by the snake"""

        # Check for invalid moves
        # e.g. moving up while the snake is moving down
        edge_case = lambda d : any([
            d == (0, 1) and self.direction == (0, -1),
            d == (0, -1) and self.direction == (0, 1),
            d == (1, 0) and self.direction == (-1, 0),
            d == (-1, 0) and self.direction == (1, 0)
        ])

        # Listen to user events and change snake direction
        if ev.type == pg.KEYDOWN:
            for key, optkey, d in zip(keys, opt_keys, directions):
                if ev.key in [key, optkey]:
                    if edge_case(d):
                        break
                    self.direction = d

    def update(self, dt):
        """
        Move the snake:
            - Add a new segment in each direction
            - Remove the last segment
        """
        sx, sy = self.snake[0].size
        if self.direction == (0, -1):
            px, py = self.snake[0].topleft
            self.snake.insert(0, pg.Rect(px, py-sy, sx, sy))
        if self.direction == (0, 1):
            px, py = self.snake[0].bottomleft
            self.snake.insert(0, pg.Rect(px, py, sx, sy))
        if self.direction == (-1, 0):
            px, py = self.snake[0].topleft
            self.snake.insert(0, pg.Rect(px-sx, py, sx, sy))
        if self.direction == (1, 0):
            px, py = self.snake[0].topright
            self.snake.insert(0, pg.Rect(px, py, sx, sy))

    def collide_target(self, target):

        if self.snake[0].colliderect(target.rect):
            target.spawn()
            return True
        else:
            del self.snake[-1]
            return False

    def collide_walls(self):
        width, height = pg.display.get_surface().get_size()
        beyond_x = self.snake[0].x > width or self.snake[0].x < 0
        beyond_y = self.snake[0].y > height or self.snake[0].y < 0
        if beyond_x or beyond_y:
            return True
        return False

    def collide_self(self):
        for seg in self.snake[1:]:
            if seg.collidepoint(self.snake[0].center):
                return True
        return False

class Target:
    def __init__(self, pos, size, color):
        self.pos = pos
        self.size = size
        self.color = color
        self.rect = None

    def draw(self, surface):
        px, py = self.pos
        sx, sy = self.size

        pg.draw.rect(surface, self.color, [px, py, sx, sy])
        pg.draw.rect(surface, pg.Color('black'), [px, py, sx, sy], 3)
        self.rect = pg.Rect(px, py, sx, sy)


    def spawn(self):
        screen = pg.display.get_surface()
        bounds = screen.get_size()

        px = random.randrange(1, (bounds[0] // GS)-1)
        py = random.randrange(2, (bounds[1] // GS)-1)
        self.pos = (px * GS, py * GS)


def draw_grid(surface):
    """
    Draw the snake playground
    """
    cx, cy = SIZE[0] // GS, SIZE[1] // GS
    for x in range(cx):
        for y in range(cy):
            pg.draw.rect(surface, pg.Color('grey'), [x*GS, y*GS, GS, GS], 1)

def draw_score(surface, score, font_size=20, pos=(10, 10)):
    font_name   = pg.font.match_font('arial')
    font        = pg.font.Font(font_name, font_size)

    tsurface    = font.render("score  " + str(score), True, pg.Color('white'))
    text_rect   = tsurface.get_rect()
    text_rect.topleft = pos
    surface.blit(tsurface, text_rect)

def draw_game_over(surface, score, font_size=20):
    pass

def main():

    # Pygame Context
    pg.init()
    pg.display.set_caption(CAPTION)
    screen  = pg.display.set_mode(SIZE, 0, 32)
    clock   = pg.time.Clock()

    # Game Objects
    snake   = Snake((225, 225), 5, pg.Color('red'))
    target  = Target((100, 100), (GS, GS), pg.Color('green'))

    # Game Variables
    score    = 0
    gameover = False

    # Game Loop
    while True:
        # Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()

                if gameover and event.key == pg.K_SPACE:
                    # -- reset items
                    score   = 0
                    snake   = Snake((225, 225), 5, pg.Color('red'))
                    target  = Target((100, 100), (GS, GS), pg.Color('green'))

                    # -- resume
                    gameover = False

            snake.event(event)

        # Draw
        screen.fill(BACKGROUND)
        if gameover:
            draw_game_over(screen, score)
        else:
            draw_score(screen, score)
            snake.draw(screen)
            target.draw(screen)

        pg.display.flip()

        # Update
        dt = clock.tick(FPS) / 1000.0
        if not gameover:
            snake.update(dt)
            if snake.collide_target(target):
                score += 1

            if snake.collide_walls() or snake.collide_self():
                gameover = True


if __name__ == '__main__':
    main()
