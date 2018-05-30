import os
import math, random
import pygame as pg
from pygame.sprite import *

# from player import Player
# from enemy import EnemySpawner

TRANSPARENT = (0, 0, 0, 0)


def random_pos(target, dist):
    pad = 100
    max_ = pg.display.get_surface().get_size()

    pos = [random.randint(0, n - pad) for n in max_]

    # Ensure the random point is more that dist away from target
    if pg.math.Vector2(pos[0] - target[0], pos[1] - target[1]).length() < dist:
        return random_pos(target, dist)
    else:
        return pos


def media_path(fn):
    path = os.path.join(os.path.dirname(__file__), 'media')
    return os.path.join(path, fn)


class Bullet(Sprite):
    def __init__(self, pos, angle, color=pg.Color('black')):
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
        self.remove()

    def remove(self):
        screen_rect = pg.display.get_surface().get_rect()
        if not self.rect.colliderect(screen_rect):
            self.kill()


class DamageBar(Sprite):
    def __init__(self, pos, size=(200, 25), color=pg.Color('green')):
        Sprite.__init__(self)

        self.size = size
        self.pos = pos
        self.color = color
        self.image = self.make_image(size)
        self.rect = self.image.get_rect(center=pos)

        self.true_pos = list(self.rect.center)

    def make_image(self, size, fill_percent=1):
        img = pg.Surface(size).convert_alpha()
        img.fill(TRANSPARENT)

        rect = img.get_rect()
        pg.draw.rect(img, pg.Color("black"), rect)

        rect2 = rect.inflate(-10, -10).copy()
        rect2.width *= fill_percent
        pg.draw.rect(img, self.color, rect2)

        return img

    def update(self, sprite):
        health_percent = sprite.health / sprite.max_health

        self.image = self.make_image(self.size, health_percent)
        self.rect = self.image.get_rect(center=self.rect.center)


class Option:
    hovered = False

    def __init__(self, text, pos, font):
        self.text = text
        self.pos = pos
        self.font = font
        self.set_rect()
        self.draw()

    def draw(self):
        self.set_rend()
        screen = pg.display.get_surface()
        screen.blit(self.rend, self.rect)

    def set_rend(self):
        self.rend = self.font.render(self.text, True, self.get_color())

    def get_color(self):
        if self.hovered:
            return (255, 255, 255)
        else:
            return (100, 100, 100)

    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.center = self.pos


class MainMenu:
    def __init__(self):
        self.font = pg.font.Font(None, 72)

        size = pg.display.get_surface().get_size()
        off_x = size[0] / 2
        off_y = size[1] / 2

        self.options = [
            Option("PLAY GAME", (off_x, off_y - 80), self.font),
            Option("CREDITS", (off_x, off_y), self.font),
            Option("EXIT", (off_x, off_y + 80), self.font)
        ]

        # Title image
        self.title = pg.image.load(media_path('title.png'))
        self.title_rect = self.title.get_rect(center=(off_x, 70))

    def draw(self, *args):
        # Draw title image
        screen = pg.display.get_surface()
        screen.blit(self.title, self.title_rect)

        # Draw Options
        for option in self.options:
            if option.rect.collidepoint(pg.mouse.get_pos()):
                option.hovered = True
            else:
                option.hovered = False

            option.draw()

    def on_mouse(self):
        for option in self.options:
            if option.rect.collidepoint(pg.mouse.get_pos()):
                return option.text


class Credits:
    def __init__(self):
        size = pg.display.get_surface().get_size()

        # Credits Text
        self._font = pg.font.Font(None, 30)
        self.text = """
            ESCAPE SHOOTER

            Author
            ````````
            Ian Ichung'wah Karanja

            Description
            `````````````
            This game was created between 1/5/17 and 3/5/17.

            The Player is challenged to kill enemies that are 
            roaming about. Proximity to the enemies triggers an 
            alert that causes them to chase and shoot at you.

            How many enemies can you kill before you die?

            Enjoy.
            """.lstrip()
        # Credits Back Button
        self.font = pg.font.Font(None, 72)
        pad_x = (size[0] - self.font.size("BACK")[0]) / 2

        self.options = [
            Option("BACK", (100, size[1] - 50), self.font),
        ]

    def draw(self, *args):
        # Draw Credits Text
        screen = pg.display.get_surface()
        size = pg.display.get_surface().get_size()

        lines = self.text.splitlines()[1:]
        for idx, l in enumerate(lines):
            # Determine x padding
            l_size = self._font.size(l)[0]
            off_x = (size[0] - l_size) / 2

            screen.blit(self._font.render(l, True, (232, 122, 49)), (off_x, 10 + (idx * 30)))

        # Draw Back button
        for option in self.options:
            if option.rect.collidepoint(pg.mouse.get_pos()):
                option.hovered = True
            else:
                option.hovered = False

            option.draw()

    def on_mouse(self):
        for option in self.options:
            if option.rect.collidepoint(pg.mouse.get_pos()):
                return option.text


class GameOver:
    def __init__(self):
        self.font = pg.font.Font(None, 72)

        self.size = pg.display.get_surface().get_size()
        off_x = self.size[0] / 2
        off_y = self.size[1] / 2

        self.options = [
            Option("RESTART", (off_x, self.size[1] - 250), self.font),
            Option("MAIN MENU", (off_x, self.size[1] - 150), self.font),
            Option("EXIT", (off_x, self.size[1] - 50), self.font)
        ]

        # Title image
        path = os.path.join(os.path.dirname(__file__), 'media')
        file = 'title.png'
        self.title = pg.image.load(os.path.join(path, file))
        self.title_rect = self.title.get_rect(center=(off_x, 70))

        # Enemies killed text
        self.font = pg.font.Font(None, 72)

    def draw(self, *args):
        off_x = self.size[0] / 2
        off_y = self.size[1] / 2

        # Draw title image
        screen = pg.display.get_surface()
        screen.blit(self.title, self.title_rect)

        # Draw Killed text
        text = " {} enemies killed !".format(args[0])
        self.killed_text = self.font.render(text, True, (230, 0, 0))
        self.killed_rect = self.killed_text.get_rect(center=(off_x, off_y - 100))
        screen.blit(self.killed_text, self.killed_rect)

        for option in self.options:
            if option.rect.collidepoint(pg.mouse.get_pos()):
                option.hovered = True
            else:
                option.hovered = False

            option.draw()

    def on_mouse(self):
        for option in self.options:
            if option.rect.collidepoint(pg.mouse.get_pos()):
                return option.text


class PauseMenu:
    def __init__(self):
        self.font = pg.font.Font(None, 72)

        size = pg.display.get_surface().get_size()
        off_x = size[0] / 2
        off_y = size[1] / 2

        text = "PAUSED"
        self.text_surf = self.font.render(text, True, (232, 122, 49))
        self.text_rect = self.text_surf.get_rect()
        self.text_rect.center = (off_x, off_y)

    def draw(self, *args):
        screen = pg.display.get_surface()
        screen.blit(self.text_surf, self.text_rect)


class MenuSystem:
    def __init__(self):

        self.active = True
        self.active_menu = 0
        self.menus = [
            MainMenu(),
            Credits(),
            GameOver(),
            PauseMenu()
        ]

        # Game State
        self.quit = False
        pg.mixer.music.load(media_path("menu_loop.wav"))
        pg.mixer.music.play(-1, 0.0)

    def draw(self, *args):
        self.menus[self.active_menu].draw(*args)

    def on_mouse(self, reset_func):
        option = self.menus[self.active_menu].on_mouse()
        if option == "PLAY GAME":
            self.active = False
        elif option == "EXIT":
            self.quit = True
        elif option == "CREDITS":
            self.set_credits()
        elif option == "BACK":
            self.set_main()
        elif option == "RESTART":
            reset_func()
            pg.mixer.music.play(-1, 0.0)
            self.active = False
        elif option == "MAIN MENU":
            reset_func()
            self.set_main()

    def set_main(self):
        self.active_menu = 0
        pg.mixer.music.play(-1, 0.0)

    def set_credits(self):
        self.active_menu = 1

    def set_gameover(self):
        self.active_menu = 2
        pg.mixer.music.stop()

    def set_pause(self):
        self.active_menu = 3
