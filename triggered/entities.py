

class Bullet(Drawable):

    def __init__(self, pos, angle,
            color=pg.Color('black')):
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

        self.collide_map()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def collide_map(self):
        walls = LevelManager.instance.get_current().MAP.walls
        for wall in walls:
            if self.rect.colliderect(wall):
                self.kill()

class Player(Drawable):

    def __init__(self, position, size):
        super(Player, self).__init__()

        self.pos    = position
        self.size   = size
        self.turret = None

        # Create Player Image
        self.original_img = self.make_image(size)
        self.surface      = self.original_img.copy()
        self.rect         = self.surface.get_rect(center=position)

        # Player Variables
        self.angle    = 0
        self.speed    = 150
        self.direction = (0, 0)
        self.bullets   = Group()
        self.rotate(pg.mouse.get_pos())

        self.ammo    = 50
        self.health  = 100
        self.damage  = 10

        self.body = pm.Body(1, 100)
        self.body.position = self.rect.center
        self.shape = pm.Circle(self.body, size[0]/2)
        self.shape.collision_type = COLLISION_MAP.get("PlayerType")
        SPACE.add(self.body, self.shape)

        display  = pg.display.get_surface()
        self.viewport = display.get_rect().copy()

    def make_image(self, size):
        img = pg.Surface(size).convert_alpha()
        img.fill(TRANSPARENT)

        rect = img.get_rect()

        self.turret = pg.draw.rect(img, pg.Color('black'), [rect.center[0] - 5, 25, 10, 50])
        pg.draw.ellipse(img, pg.Color('black'), rect.inflate(-10, -10))
        pg.draw.ellipse(img, pg.Color('tomato'), rect.inflate(-20, -20))

        return img

    def rotate(self, pos):
        offset = (pos[1] - self.rect.centery, pos[0] - self.rect.centerx)
        self.angle = 90 - math.degrees(math.atan2(*offset))

        self.surface = pg.transform.rotate(self.original_img, self.angle)
        self.rect = self.surface.get_rect(center=self.rect.center)

    def shoot(self):
        if self.ammo <= 0:
            return
        self.ammo -= 1

        pos = pg.mouse.get_pos()
        px, py, *_ = self.viewport
        pos = pos[0] + px, pos[1] + py

        vec = vec2(pos[0] - self.rect.centerx, pos[1] - self.rect.centery).normalize()
        gun_pos = vec2(self.rect.center) + (vec * vec2(self.turret.center).length()/2)
        self.bullets.add(Bullet(gun_pos, self.angle))

    def check_health(self):
        if self.health <= 0:
            SceneManager.instance.switch(LevelFailed.NAME)
            # self.kill()
            # _map = LevelManager.instance.get_current().MAP
            # _map.remove(self)

    def hit(self):
        """ Called when enemy bullet hits us (see Enemy Class)"""
        self.health -= self.damage

    def draw_ammo(self, surface):
        """ Draw ammo on top-right corner of screen"""
        # - draw one clip for every ten bullets
        rect = surface.get_rect()
        for i in range(self.ammo // 10):
            pg.draw.rect(surface, pg.Color("yellow"),
                    [500 + (i*15), 5, 10, 25]
                )

    def draw(self, surface):
        surface.blit(self.surface, self.rect)
        self.bullets.draw(surface)
        # self.draw_ammo(surface)

    def event(self, event):
        if not isinstance(SceneManager.instance.current, GameScene): return
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.shoot()

    def update(self, dt):
        self.bullets.update(dt)

        # Keys and mouse
        pos = pg.mouse.get_pos()
        keys = pg.key.get_pressed()

        # -- Rotate
        px, py, *_ = self.viewport
        pos = pos[0] + px, pos[1] + py
        vec = vec2(pos[0] - self.rect.centerx, pos[1] - self.rect.centery)
        if vec.length() > 5:
            self.rotate(pos)
            pass

        # -- Move
        dx, dy = 0, 0
        for key, _dir in IMPUT_MAP.items():
            if keys[key]:
                dx, dy = _dir

        # -- running
        speed = self.speed
        if keys[pg.K_RSHIFT] or keys[pg.K_LSHIFT]:
            speed *= 1.5

        bx, by = self.body.position
        bx += dx * speed * dt
        by += dy * speed * dt

        self.body.position = (bx, by)
        self.rect.center = (bx, by)

        self.check_health()

class EnemyState(Enum):
    IDLE    = 0
    PATROL  = 1
    CHASE   = 2
    ATTACK  = 3

class Enemy(Drawable):

    def __init__(self, position, size,
                    waypoints=None):
        super(Enemy, self).__init__()

        self.pos   = position
        self.size  = size
        self.state = EnemyState.IDLE
        self.speed = 75
        self.turret = None

        self.original_img = self.make_image()
        self.surface      = self.original_img.copy()
        self.rect         = self.surface.get_rect(center=position)

        self.waypoints = it.cycle(waypoints)
        self.target    = next(self.waypoints)

        self.patrol_epsilon = 2
        self.chase_radius   = 300
        self.attack_radius  = 100

        self.attack_frequency = 50
        self.current_attack   = 0

        self.angle   = 0
        self.bullets = Group()

        self.health  = 100
        self.damage  = 15

        self.body = pm.Body(1, 100)
        self.body.position = self.rect.center
        self.shape = pm.Circle(self.body, size[0]/2)
        self.shape.collision_type = COLLISION_MAP.get("EnemyType")
        SPACE.add(self.body, self.shape)


    def make_image(self):
        img = pg.Surface(self.size).convert_alpha()
        img.fill(TRANSPARENT)

        rect = img.get_rect()
        center = rect.center

        self.turret = pg.draw.rect(img, pg.Color('black'), [center[0] - 5, 40, 10, 40])
        pg.draw.ellipse(img, pg.Color('black'), rect.inflate(-10, -10))
        pg.draw.ellipse(img, pg.Color('green'), rect.inflate(-20, -20))
        return img

    def draw(self, surface):
        surface.blit(self.surface, self.rect)
        self.bullets.draw(surface)

    def update(self, dt):
        player = LevelManager.instance.get_current().get_player()
        player_distance = (vec2(self.rect.center) - vec2(player.rect.center)).length_squared()

        # if player_distance < self.chase_radius**2:
        #     self.state = EnemyState.CHASE
        # else:
        #     self.state = EnemyState.PATROL

        # if player_distance < self.attack_radius**2:
        #     self.state = EnemyState.ATTACK

        if self.state == EnemyState.IDLE:
            self.state = EnemyState.PATROL
        elif self.state == EnemyState.PATROL:
            self.patrol(dt)
        elif self.state == EnemyState.CHASE:
            self.chase(player.rect.center, dt)
            pass
        elif self.state == EnemyState.ATTACK:
            self.attack(player.rect.center)

        self.bullets.update(dt)
        bx, by = self.body.position
        self.rect.center = (bx, by)

        self.check_shot_at(player)
        if self.health <= 0:
            self.kill()
            SPACE.remove(self.shape, self.body)
            _map = LevelManager.instance.get_current().MAP
            _map.remove(self)


    def patrol(self, dt):
        diff     = vec2(self.rect.center) - vec2(self.target)
        distance = diff.length_squared()
        if distance < self.patrol_epsilon:
            self.target = next(self.waypoints)

        self.look_at(self.target)
        self.move_to_target(self.target, dt)

    def chase(self, player_pos, dt):
        self.look_at(player_pos)
        self.move_to_target(player_pos, dt)

    def attack(self, player):
        self.look_at(player)
        self.current_attack += 1

        if self.current_attack == self.attack_frequency:
            vec = vec2(player[0] - self.rect.centerx, player[1] - self.rect.centery).normalize()
            gun_pos = vec2(self.rect.center) + (vec * vec2(self.turret.center).length()/2)
            self.bullets.add(Bullet(gun_pos, self.angle))

            self.current_attack = 0

    def move_to_target(self, target, dt):
        diff      = vec2(target) - vec2(self.rect.center)
        if diff.length_squared():
            dx, dy = diff.normalize()

            bx, by = self.body.position
            bx += dx * self.speed * dt
            by += dy * self.speed * dt
            self.body.position = (bx, by)

    def look_at(self, target):
        offset = (target[1] - self.rect.centery, target[0] - self.rect.centerx)
        self.angle  = 90 - math.degrees(math.atan2(*offset))

        self.surface = pg.transform.rotate(self.original_img, self.angle)
        self.rect    = self.surface.get_rect(center=self.rect.center)

    def check_shot_at(self, player):

        # Check if player bullets hit us
        for bullet in player.bullets:
            if self.rect.colliderect(bullet.rect):
                self.health -= self.damage
                bullet.kill()

        # Check if our bullets hit the player
        for bullet in self.bullets:
            if player.rect.colliderect(bullet.rect):
                player.hit()
                bullet.kill()
