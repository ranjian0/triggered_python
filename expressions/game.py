import os
import pickle
import pygame as pg
from pathlib import Path
from board import Board
from utils import Timer, MainMenu, GameOver

BACKGROUND_COLOR = pg.Color("darkslategrey")
FPS = 60


class Game:
    """Class responsible for program control flow."""

    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()

        # Game Objects
        self.main_menu = MainMenu(self.screen)
        self.game_over = GameOver(self.screen)
        self.timer = Timer((5, 5), self.screen_rect)
        self.board = Board(self.screen_rect)
        self.score = self.font = pg.font.Font(None, 30)

        # Game Vars
        self.done = False
        self.GAME_SCORE = 0

    def play_game(self):
        self.main_menu.active = False
        self.timer.reset()
        self.board.reset()
        self.board.board_score = 0

    def restart(self):
        self.game_over.active = False
        self.timer.reset()
        self.board.reset()
        self.board.board_score = 0

    def exit_game(self):
        self.done = True

    def m_menu(self):
        self.main_menu.active, self.game_over.active = True, False

    def check_high_score(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(cur_dir, 'game.data')

        if Path(data_file).exists():
            data = pickle.load(open(data_file, 'rb'))
            if data['highscore'] < self.GAME_SCORE:
                with open(data_file, 'wb') as file:
                    pickle.dump({'highscore' : self.GAME_SCORE}, file)
        else:
            with open(data_file, 'wb') as file:
                pickle.dump({'highscore' : self.GAME_SCORE}, file)

    def get_high_score(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(cur_dir, 'game.data')
        if Path(data_file).exists():
            return pickle.load(open(data_file, 'rb'))['highscore']
        else:
            return 0

    def event_loop(self):
        """Basic event loop."""
        for event in pg.event.get():
            # Menu Events
            if self.main_menu.active:
                self.main_menu.on_event(event)
            if self.game_over.active:
                self.game_over.on_event(event)

            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.MOUSEBUTTONDOWN:
                self.board.on_mouse(event.pos, self.timer)

    def update(self, dt):
        """Update must accept and pass dt to all elements that need to update."""

        if self.main_menu.active:
            if self.get_high_score() > 0:
                txt = """
                HIGHSCORE
                {}
                """.format(self.get_high_score())
                self.main_menu.highscore.text = txt

            self.main_menu.play_btn.on_click(self.play_game)
            self.main_menu.exit_btn.on_click(self.exit_game)
            self.main_menu.update()
        elif self.game_over.active:
            self.check_high_score()
            self.game_over.score.text = "SCORE {}".format(self.GAME_SCORE)

            self.game_over.restart_btn.on_click(self.restart)
            self.game_over.mm_btn.on_click(self.m_menu)
            self.game_over.exit_btn.on_click(self.exit_game)
            self.game_over.update()
        else:
            # Update timer
            if self.timer.timer_size <= 0:
                self.game_over.active = True
            self.timer.update(dt)

            # Update Board
            self.board.update()
            self.GAME_SCORE = self.board.board_score

    def render(self):
        """Render all needed elements and update the display."""
        if self.main_menu.active:
            self.main_menu.draw()
        elif self.game_over.active:
            self.game_over.draw()
        else:
            self.screen.fill(BACKGROUND_COLOR)

            # Score
            score_surf = self.score.render("Score  {} ".format(self.GAME_SCORE), True, (255, 255, 255))
            self.screen.blit(score_surf, (self.screen_rect.width - 100, 5))

            self.timer.draw(self.screen)
            self.board.draw(self.screen)

        pg.display.update()

    def main_loop(self):
        """Call all the individual game components in order."""
        dt = 0
        self.clock.tick(FPS)
        while not self.done:
            self.event_loop()
            self.update(dt)
            self.render()
            dt = self.clock.tick(FPS) / 1000.0
