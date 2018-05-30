import math, random
import pygame as pg
from pygame.sprite import *

from utils import Bullet, media_path

TRANSPARENT = (0, 0, 0, 0)


class Player(Sprite):
    def __init__(self, pos, size):
        Sprite.__init__(self)

        # Create Player Image
        self.original_img = self.make_image(size)
        self.image = self.original_img.copy()
        self.rect = self.image.get_rect(center=pos)

        # Player Variables
        self.true_pos = list(self.rect.center)
        self.angle = 0
        self.speed = 200
        self.bullets = Group()
        self.rapid_fire = 0

        # Health
        self.max_health = 100
        self.health = 100

        # Sounds
        self.shoot = pg.mixer.Sound(media_path('gunshot.wav'))
        self.hit = pg.mixer.Sound(media_path('hit.wav'))

    def make_image(self, size):

        img = pg.Surface(size).convert_alpha()
        img.fill(TRANSPARENT)
        rect = img.get_rect()

        pg.draw.rect(img, pg.Color('black'), [rect.center[0] - 5, 25, 10, 50])
        pg.draw.ellipse(img, pg.Color('black'), rect.inflate(-10, -10))
        pg.draw.ellipse(img, pg.Color('tomato'), rect.inflate(-20, -20))

        return img

    def update(self, dt):
        # Keys and mouse
        pos = pg.mouse.get_pos()
        keys = pg.key.get_pressed()

        # Movement
        vec = pg.math.Vector2(pos[0] - self.true_pos[0], pos[1] - self.true_pos[1])
        if vec.length() > 5:
            # Rotate towards the mouse cursor
            self.rotate(pos)

            # Move towards the mouse cursor
            direction = vec.normalize()
            if keys[pg.K_w]:
                self.true_pos[0] += direction[0] * self.speed * dt
                self.true_pos[1] += direction[1] * self.speed * dt
            if keys[pg.K_s]:
                self.true_pos[0] -= direction[0] * self.speed * dt
                self.true_pos[1] -= direction[1] * self.speed * dt
            self.rect.center = self.true_pos

        # Keep the player within the screen area
        self.clamp()

        # Update bullets
        self.bullets.update(dt)

        # Rapid fire:

        if pg.mouse.get_pressed()[2]:
            if self.rapid_fire % 10 == 0:
                self.shoot_bullet()

            self.rapid_fire += 1

    def rotate(self, pos):
        offset = (pos[1] - self.rect.centery, pos[0] - self.rect.centerx)
        self.angle = 90 - math.degrees(math.atan2(*offset))

        self.image = pg.transform.rotate(self.original_img, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot_bullet(self):
        self.shoot.play()
        pos = pg.mouse.get_pos()
        vec = pg.math.Vector2(pos[0] - self.true_pos[0], pos[1] - self.true_pos[1]).normalize()
        gun_pos = (self.rect.centerx + (vec.x * 25), self.rect.centery + (vec.y * 25))

        self.bullets.add(Bullet(gun_pos, self.angle))

    def clamp(self):
        screen_rect = pg.display.get_surface().get_rect()
        if not screen_rect.contains(self.rect):
            self.rect.clamp_ip(screen_rect)
            self.true_pos = list(self.rect.center)

    def check_collision(self, enemies):

        for enemy in enemies:
            # Check if enemy has bullets
            if enemy.bullets:
                for bullet in enemy.bullets.sprites():
                    if self.rect.colliderect(bullet.rect):
                        # self.hit.play()
                        bullet.kill()
                        self.health -= 5
