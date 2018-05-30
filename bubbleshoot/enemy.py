import math, random
import pygame as pg
from pygame.sprite import *

from player import Bullet
from utils import DamageBar, random_pos, media_path

TRANSPARENT = (0, 0, 0, 0)


class EnemySpawner:
    """ Spawn new enemy objects every spawn interval"""

    def __init__(self):
        self.time = 0
        self.spawn_interval = 250
        self.enemies = Group()

        self.enemies_killed = 0
        self.spawn_sound = pg.mixer.Sound(media_path('spawn.wav'))

    def spawn(self, player_pos):
        self.spawn_sound.play()
        # Calculate random position for spawning enemies
        spawn_offset = 100
        rand_pos = random_pos(player_pos, spawn_offset)

        # Add Enemies to sprite group
        e = Enemy(rand_pos, (50, 50))
        self.enemies.add(e)

    def update(self, dt, player_pos):
        # Spawn when time is zero and after every 5 secs (roughy 5 seconds)
        if self.time == 50 or (self.time > 100 and (self.time % self.spawn_interval) == 0):
            self.spawn(player_pos)
        self.time += 1

        # Update sprites
        self.enemies.update(dt, player_pos)

        for enemy in self.enemies.sprites():
            if enemy.killed:
                self.enemies_killed += 1
                enemy.kill()


class Enemy(Sprite):
    """ Create enemy object and behaviour """

    def __init__(self, pos, size):
        Sprite.__init__(self)
        self.size = size

        self.original_img = self.make_image(self.size, pg.Color('green'))
        self.image = self.original_img.copy()
        self.rect = self.image.get_rect(center=pos)

        self.true_pos = list(self.rect.center)
        self.speed = 100
        self.max_health = 100
        self.health = 100
        self.killed = False
        self.damage_bar = DamageBar(self.rect.topleft, (50, 10), pg.Color('red'))

        # Patrol Varialbles
        self.patrol_radius = 200
        self.patrol_points = []
        self.current_patrol = 0

        # Bullet Variables
        self.bullets = Group()
        self.bullet_interval = 50
        self.bullet_time = 0

        self.shoot = pg.mixer.Sound(media_path('enemy_gunshot.wav'))

    def make_image(self, size, player_color):

        img = pg.Surface(size).convert_alpha()
        img.fill(TRANSPARENT)

        rect = img.get_rect()
        center = rect.center

        pg.draw.rect(img, pg.Color('black'), [center[0] - 5, 40, 10, 40])
        pg.draw.ellipse(img, pg.Color('black'), rect.inflate(-10, -10))
        pg.draw.ellipse(img, player_color, rect.inflate(-20, -20))
        return img

    def update(self, dt, player_pos):
        # Create enemy behaviour
        # 1. Patrol - enemy moves through random points
        # 2. Chase and attack - enemy follows player around and shoots at him/her

        # If the enemy is more than patrol_radius units away from player
        # do patrol
        dist_vec = pg.math.Vector2(self.rect.center) - pg.math.Vector2(player_pos)
        if dist_vec.length() >= self.patrol_radius:
            # Change color of player image
            self.original_img = self.make_image(self.size, pg.Color("green"))
            self.image = self.original_img.copy()

            self.patrol(dt)
        else:
            # Change color of player image
            self.original_img = self.make_image(self.size, pg.Color("red"))
            self.image = self.original_img.copy()
            # Chase and shoot the player
            self.chase(dt, player_pos)

            # Clear the patrol points and reset current_patrol
            self.patrol_points.clear()
            self.current_patrol = 0

        # Keep sprites within screen area
        self.clamp()

        # Update damage bar
        pos = (self.rect.topleft[0] + 10, self.rect.topleft[1])
        self.damage_bar.rect.center = pos
        self.damage_bar.update(self)

        # Update bullets
        self.bullets.update(dt)

        # Check if we have health
        if self.health <= 0:
            self.killed = True

    def patrol(self, dt):
        # Create patrol point if we ran out
        if len(self.patrol_points) <= self.current_patrol:
            range_ = 100
            nxt_patrol = random_pos(self.rect.center, range_)

            self.patrol_points.append(nxt_patrol)

        # Move to the current patrol point
        cpoint = self.patrol_points[self.current_patrol]
        self.move_to(cpoint, dt)

        # Update patrol point if we reached it
        if pg.math.Vector2(cpoint[0] - self.rect.centerx, cpoint[1] - self.rect.centery).length() < 10:
            self.current_patrol += 1

    def chase(self, dt, player_pos):
        # Chase the player
        # 1. Look towards the player
        self.rotate(player_pos)

        # 2. Shoot the player
        self.shoot_bullet()

        # 3. Follow the player
        self.move_to(player_pos, dt, isPlayer=True)

    def move_to(self, pos, dt, isPlayer=False):
        # Move towards vec pos

        # Point towards target
        self.rotate(pos)

        # Calculate distance between current pos and target, and direction
        vec = pg.math.Vector2(pos[0] - self.true_pos[0], pos[1] - self.true_pos[1])
        direction = vec.normalize()

        # Progress towards the target
        if vec.length() > 10:
            self.true_pos[0] += direction[0] * self.speed * dt
            self.true_pos[1] += direction[1] * self.speed * dt

            vec = pg.math.Vector2(pos[0] - self.true_pos[0], pos[1] - self.true_pos[1])
            self.rect.center = self.true_pos
        else:
            # If the target is not a player, increment current_patrol if reached
            if not isPlayer:
                self.current_patrol += 1

    def rotate(self, pos):
        offset = (pos[1] - self.rect.centery, pos[0] - self.rect.centerx)
        self.angle = 90 - math.degrees(math.atan2(*offset))

        self.image = pg.transform.rotate(self.original_img, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot_bullet(self):
        if self.bullet_time % self.bullet_interval == 0:
            self.shoot.play()
            pos = pg.mouse.get_pos()
            vec = pg.math.Vector2(pos[0] - self.true_pos[0], pos[1] - self.true_pos[1]).normalize()
            gun_pos = (self.rect.centerx + (vec.x * 25), self.rect.centery + (vec.y * 25))

            b = Bullet(gun_pos, self.angle, color=pg.Color('red'))
            self.bullets.add(b)
        self.bullet_time += 1

    def clamp(self):
        screen_rect = pg.display.get_surface().get_rect()
        if not screen_rect.contains(self.rect):
            self.rect.clamp_ip(screen_rect)
            self.true_pos = list(self.rect.center)

    def check_collision(self, player):
        # Check for collision with player
        if self.rect.colliderect(player.rect):
            # Resolve collision
            self.speed = 0
        else:
            self.speed = 100

        # Check for collicion with player bullets
        if player.bullets:
            for bullet in player.bullets:
                if self.rect.colliderect(bullet.rect):
                    bullet.kill()
                    self.health -= 10
