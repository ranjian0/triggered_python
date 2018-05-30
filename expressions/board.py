import random
import pygame as pg
from collections import Counter


class Tile:
    TILE_SIZE = (100, 100)

    def __init__(self, pos, value):
        self.pos = pos
        self.value = value

        self.tile = self.make_image()
        self.tile_rect = self.tile.get_rect(center=self.pos)
        self.text, self.text_rect = self.make_text()

        # Tile states
        self.default = True
        self.hover = False

    def make_image(self, border_color=pg.Color('black'), fill_color=pg.Color('tomato')):
        image = pg.Surface(self.TILE_SIZE).convert_alpha()
        image.fill((0, 0, 0, 0))
        rect = image.get_rect()

        pg.draw.ellipse(image, border_color, rect)
        pg.draw.ellipse(image, fill_color, rect.inflate(-12, -12))

        return image

    def make_text(self):
        font = pg.font.SysFont('sans serif', 50)
        label = font.render(str(self.value), True, pg.Color("black"))
        label_rect = label.get_rect(center=self.pos)

        return label, label_rect

    def draw(self, surface):
        surface.blit(self.tile, self.tile_rect)
        surface.blit(self.text, self.text_rect)

    def update(self):
        pos = pg.mouse.get_pos()
        if self.tile_rect.collidepoint(pos):
            self.hover = True
        else:
            self.default = True

        # Change the tile appearance
        if self.default:
            self.tile = self.make_image(pg.Color('black'))
            self.tile_rect = self.tile.get_rect(center=self.pos)
        if self.hover:
            self.tile = self.make_image(pg.Color('white'))
            self.tile_rect = self.tile.get_rect(center=self.pos)

        self.default, self.hover = (False, False)


class Target(object):
    def __init__(self, pos):
        self.pos = pos
        self.value = self.generate_expression()
        self.text, self.text_rect = self.setup_font()

    def setup_font(self):
        font = pg.font.SysFont('timesnewroman', 25)
        label = font.render(str(self.value), True, pg.Color("white"))
        label_rect = label.get_rect(center=self.pos)

        return label, label_rect

    def draw(self, surface):
        surface.blit(self.text, self.text_rect)

    def reset(self):
        self.value = self.generate_expression()
        self.text, self.text_rect = self.setup_font()

    def generate_expression(self):
        fnum, snum = [random.randint(0, 50) for _ in range(2)]

        if fnum < snum:
            fnum, snum = snum, fnum
        operation = random.choice(['+', '-', '*'])

        text = "{0} {1} {2}".format(fnum, operation, snum)
        self.result = eval(text)

        return text


class Board(object):
    TILE_SIZE = (100, 100)

    def __init__(self, screen_rect):
        self.screen_rect = screen_rect
        self.tiles = []
        self.target = Target(screen_rect.center)

        self.make_board()
        self.board_score = 0

    def make_board(self):
        self.target.reset()
        positions = self.tile_positions()
        values = self.tile_values()

        for pos in positions:
            rand_value = values[positions.index(pos)]
            t = Tile(pos, rand_value)
            self.tiles.append(t)

    def tile_positions(self):
        # Create positions for top, left, bottom and right part of screen
        positions = [(self.screen_rect.size[0] * .5, self.screen_rect.size[1] * .25),  # TOP
                     (self.screen_rect.size[0] * .75, self.screen_rect.size[1] * .5),  # RIGHT
                     (self.screen_rect.size[0] * .5, self.screen_rect.size[1] * .75),  # BOTTOM
                     (self.screen_rect.size[0] * .25, self.screen_rect.size[1] * .5)]  # LEFT

        return positions

    def tile_values(self):
        res = self.target.result
        values = [0, 0, 0, 0]
        values[random.randint(0, len(values) - 1)] = round(res, 2)

        epsilon = int(res + (res / 2))
        for idx, v in enumerate(values):
            if v == 0:
                rvalue = random.randint(res, epsilon)
                values[idx] = rvalue

        def remove_duplicates(vals):
            duplicate, count = Counter(vals).most_common(1)[0]
            for i in range(count - 1):
                r = random.randint(0, 10)
                vals[vals.index(duplicate)] += r

            if len(values) > len(set(values)):
                return remove_duplicates(values)
            return values

        # Remove duplicates
        if len(values) > len(set(values)):
            values = remove_duplicates(values)
        return values

    def reset(self):
        self.tiles.clear()
        self.make_board()

    def on_mouse(self, pos, t):
        for tile in self.tiles:
            if tile.tile_rect.collidepoint(*pos):
                if tile.value == self.target.result:
                    self.board_score += 1
                    t.add_timer(25)
                    self.reset()
                else:
                    pass

    def draw(self, surface):
        self.target.draw(surface)
        for tile in self.tiles:
            tile.draw(surface)

    def update(self):
        for tile in self.tiles:
            tile.update()
