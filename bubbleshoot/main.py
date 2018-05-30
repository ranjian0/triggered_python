import os, sys, math
import pygame as pg

from player import Player
from enemy import EnemySpawner
from utils import DamageBar, MenuSystem, media_path

TITLE = "Bubble Shoot"
SIZE = (0, 0)
FPS = 60

BACKGROUND = (80, 80, 80)
MENU_BACKGROUND = (55, 37, 92)


class Game:
    def __init__(self):
        pg.init()
        SIZE = pg.display.Info().current_w, pg.display.Info().current_h - 100
        pg.display.set_caption(TITLE)
        self.screen = pg.display.set_mode(SIZE, pg.RESIZABLE, 32)

        # Create sprites
        self.player = Player([n / 2 for n in SIZE], (50, 50))
        self.espawner = EnemySpawner()
        self.damage_bar = DamageBar((110, 20), (200, 25))
        self.menu = MenuSystem()

        # Game vars
        self.score = 0
        self.font = pg.font.Font(None, 30)

        # Load cursor
        self.game_cursor = pg.cursors.load_xbm(media_path("cursor.xbm"), media_path("cursor-mask.xbm"))

    def reset(self):
        self.espawner.enemies_killed = 0
        for obj in [self.player, self.espawner]:
            if isinstance(obj, Player):
                obj.health = obj.max_health
                obj.bullets.empty()

            if isinstance(obj, EnemySpawner):
                obj.time = 0
                obj.enemies.empty()

    def events(self):
        for event in pg.event.get():
            # Quit Events
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False

            # Resize Events
            if event.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode(event.dict['size'], pg.RESIZABLE, 32)
                pg.display.update()

            # Pause Menu
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                if not self.menu.active:
                    self.menu.set_pause()
                    self.menu.active = True
                else:
                    self.menu.active = False

            # Menu and Player Events
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.menu.active:
                        self.menu.on_mouse(self.reset)
                    else:
                        self.player.shoot_bullet()

    def draw(self):

        if self.menu.active:
            self.screen.fill(MENU_BACKGROUND)
            pg.mouse.set_cursor(*pg.cursors.arrow)

            self.menu.draw(self.score)
        else:
            self.screen.fill(BACKGROUND)
            pg.mouse.set_cursor(*self.game_cursor)

            # Draw Player DamageBar
            self.screen.blit(self.damage_bar.image, self.damage_bar.rect)

            # Draw Score
            size = pg.display.get_surface().get_size()
            score_surf = self.font.render("Score  {} ".format(self.score), True, (255, 255, 255))
            self.screen.blit(score_surf, (size[0] - 200, 15))

            # Draw player and player bullets
            self.screen.blit(self.player.image, self.player.rect)
            self.player.bullets.draw(self.screen)

            # Draw enemies and enemy bullets, damage_bars
            self.espawner.enemies.draw(self.screen)
            for enemy in self.espawner.enemies.sprites():
                enemy.bullets.draw(self.screen)
                self.screen.blit(enemy.damage_bar.image, enemy.damage_bar.rect)

        pg.display.update()

    def update(self, dt):

        if not self.menu.active:
            # Update player and score
            self.player.update(dt)
            self.score = self.espawner.enemies_killed

            # Update damage_bar
            self.damage_bar.update(self.player)

            # Update enemies
            self.espawner.update(dt, self.player.rect.center)

            # Check collisions
            self.player.check_collision(self.espawner.enemies)
            for enemy in self.espawner.enemies:
                enemy.check_collision(self.player)

            # Check Player Death
            if self.player.health <= 0:
                self.menu.set_gameover()
                self.menu.active = True
        else:
            if self.menu.quit:
                self.running = False

    def run(self):
        self.running = True
        self.clock = pg.time.Clock()
        dt = 0

        self.clock.tick(FPS)
        while self.running:
            self.events()
            self.draw()
            self.update(dt)
            dt = self.clock.tick(FPS) / 1000.0


if __name__ == '__main__':
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    g = Game()
    g.run()

    pg.quit()
    sys.exit()
