import pygame as pg
from pgmenu import Menu, Label, Button, MultiLineLabel

class Timer:
    TIMER_SIZE = None

    def __init__(self, pos, screen_rect):
        self.pos = pos
        self.TIMER_SIZE = (screen_rect.size[0] / 2, 25)

        self.timer = self.make_timer()
        self.timer_rect = self.timer.get_rect()

        self.max_timer_size = self.TIMER_SIZE[0] - 15
        self.timer_size = self.TIMER_SIZE[0] - 15

    def make_timer(self):
        img = pg.Surface(self.TIMER_SIZE).convert_alpha()
        img.fill((0, 0, 0, 0))

        pg.draw.rect(img, pg.Color("black"),
                     (self.pos[0], self.pos[1], self.TIMER_SIZE[0], self.TIMER_SIZE[1]))
        pg.draw.rect(img, pg.Color("green"),
                     (self.pos[0] + 5, self.pos[1] + 5, self.TIMER_SIZE[0] - 15, self.TIMER_SIZE[1] - 15))

        return img

    def draw(self, surface):
        surface.blit(self.timer, self.timer_rect)

    def update(self, dt):
        self.remake_timer(dt)

    def reset(self):
        self.timer_size = self.max_timer_size

    def remake_timer(self, dt):
        img = pg.Surface(self.TIMER_SIZE).convert_alpha()
        img.fill((0, 0, 0, 0))

        self.timer_size -= dt * 10
        pg.draw.rect(img, pg.Color("black"), (self.pos[0], self.pos[1], self.TIMER_SIZE[0], self.TIMER_SIZE[1]))
        pg.draw.rect(img, pg.Color("green"),
                     (self.pos[0] + 5, self.pos[1] + 5, self.timer_size, self.TIMER_SIZE[1] - 15))

        self.timer = img
        self.timer_rect = self.timer.get_rect()

    def add_timer(self, d):

        if (self.timer_size + d) > self.max_timer_size:
            self.timer_size = self.max_timer_size
        else:
            self.timer_size += d


class MainMenu(Menu):
    active = True

    def __init__(self, screen):
        Menu.__init__(self, screen)

        # Add background Color
        self.color = pg.Color("grey")

        # Add widgets
        self.title = Label((250, 50), "EXPRESSIONS", font_size=70, font_color=pg.Color("maroon"))
        self.play_btn = Button((250, 150), (250, 50), "PLAY", pg.Color("white"), pg.Color("maroon"), pg.Color("red"))
        self.exit_btn = Button((250, 250), (250, 50), "EXIT", pg.Color("white"), pg.Color("maroon"), pg.Color("red"))
        credit = """
        Created by
        Ian Ichung'wah Karanja
        @2017
        """
        self.credit = MultiLineLabel((0, 0), credit, valign="BOTTOM", font_size=18)
        self.highscore = MultiLineLabel((150, 0), "", valign="BOTTOM", font_size=20, font_color=pg.Color("red"))

        # Add widgets to menu canvas
        self.add(self.title)
        self.add(self.play_btn)
        self.add(self.exit_btn)
        self.add(self.credit)
        self.add(self.highscore)


class GameOver(Menu):
    active = False

    def __init__(self, screen):
        Menu.__init__(self, screen)

        # Add background Color
        self.color = pg.Color("grey")

        # Add widgets
        self.score = Label((250, 50), "", font_size=56, font_color=pg.Color("red"))
        self.restart_btn = Button((250, 150), (250, 50), "RESTART", pg.Color("white"), pg.Color("maroon"),
                                  pg.Color("red"))
        self.mm_btn = Button((250, 250), (250, 50), "MAIN MENU", pg.Color("white"), pg.Color("maroon"), pg.Color("red"))
        self.exit_btn = Button((250, 350), (250, 50), "EXIT", pg.Color("white"), pg.Color("maroon"), pg.Color("red"))
        credit = """
        Created by
        Ian Ichung'wah Karanja
        @2017
        """
        self.credit = MultiLineLabel((0, 0), credit, valign="BOTTOM", font_size=18)

        # Add widgets to menu canvas
        self.add(self.score)
        self.add(self.mm_btn)
        self.add(self.restart_btn)
        self.add(self.exit_btn)
        self.add(self.credit)
