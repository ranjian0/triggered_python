import sys
import random
import pygame as pg
import pymunk as pm

from pymunk import pygame_util as putils

FPS         = 60
SIZE        = 400, 500
CAPTION     = "Flappy Bird"
BACKGROUND  = (100, 100, 100)

PHYSICS_STEP  = 50
COLLISION_MAP = {
    "BirdType"   : 1,
    "BlockType"  : 2,
    "GroundType" : 3,
    "PointType"  : 4
}

putils.positive_y_is_up = False

EVENT_MAP = {
    "ScoreEvent"    : pg.USEREVENT + 1,
    "GameOverEvent" : pg.USEREVENT + 2,
}

def main():
    pg.init()
    pg.display.set_caption(CAPTION)
    score = 0

    screen = pg.display.set_mode(SIZE, 0, 32)
    clock  = pg.time.Clock()

    space = pm.Space()
    space.gravity = (0.0, 20.0)

    bird   = Bird(20, (150, 200), space)
    blocks = Blocks(space=space)

    gamestarted = False
    gameover    = False

    add_ground(space)
    setup_collisions(space, blocks, bird)

    while True:

        # -- Events
        for event in pg.event.get():
            QUIT_COND = [
                event.type == pg.QUIT,
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE]

            if any(QUIT_COND):
                pg.quit()
                sys.exit()

            if event.type == EVENT_MAP.get("ScoreEvent"):
                score += 1

            if event.type == EVENT_MAP.get("GameOverEvent"):
                gameover = True

            if not gamestarted:
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    gamestarted = True

            if gameover:
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    bird.reset()
                    blocks.reset()
                    score = 0
                    gameover = False

            bird.event(event)

        # -- Draw
        screen.fill(BACKGROUND)

        if gameover:
            draw_game_over(screen, score)
            pg.display.flip()
            continue

        if gamestarted:
            bird.draw(screen)
            blocks.draw(screen)
            draw_score(screen, score)
        else:
            draw_start_screen(screen)


        # options = putils.DrawOptions(screen)
        # space.debug_draw(options)

        pg.display.flip()

        # -- Update
        # print(clock.get_fps())
        dt = clock.tick(FPS) / 1000.0
        if gamestarted:
            for _ in range(PHYSICS_STEP):
                space.step(0.1 / PHYSICS_STEP)
            bird.update(dt)
            blocks.update(dt, bird)

def post_score():
    score_event = pg.event.Event(EVENT_MAP.get("ScoreEvent"))
    pg.event.post(score_event)

def post_gameover():
    over_event = pg.event.Event(EVENT_MAP.get("GameOverEvent"))
    pg.event.post(over_event)

def draw_start_screen(surface):
    font_name   = pg.font.match_font('arial')

    # -- title
    font = pg.font.Font(font_name, 40)
    font.set_bold(True)

    surf = font.render(CAPTION, True, pg.Color("yellow"))
    rect = surf.get_rect()
    rect.center = (SIZE[0]//2, 50)
    surface.blit(surf, rect)

    # -- instructions
    font = pg.font.Font(font_name, 25)

    txt = "Space to Start"
    surf = font.render(txt, True, pg.Color("white"))
    rect = surf.get_rect()
    rect.center = (SIZE[0]//2, SIZE[1]//2)
    surface.blit(surf, rect)

def draw_game_over(surface, score):
    font_name   = pg.font.match_font('arial')

    # -- Draw Game Over Text
    font        = pg.font.Font(font_name, 40)
    font.set_bold(True)

    tsurface    = font.render("GAME OVER", True, pg.Color('red'))
    text_rect   = tsurface.get_rect()
    text_rect.center = (SIZE[0]//2, 100)
    surface.blit(tsurface, text_rect)


    # -- Draw score text
    font        = pg.font.Font(font_name, 20)
    font.set_bold(True)

    tsurface    = font.render("Your Score " + str(score), True, pg.Color('white'))
    text_rect   = tsurface.get_rect()
    text_rect.center = (SIZE[0]//2, 200)
    surface.blit(tsurface, text_rect)

    # -- Draw instructions
    font        = pg.font.Font(font_name, 12)
    font.set_bold(True)
    font.set_italic(True)

    tsurface    = font.render("Press Escape to QUIT, Space to RESTART", True, pg.Color('white'))
    text_rect   = tsurface.get_rect()
    text_rect.center = (SIZE[0]//2, SIZE[1]-20)
    surface.blit(tsurface, text_rect)

def draw_score(surface, score):
    font_name   = pg.font.match_font('arial')
    options = [
        ("Score",    12, (25, 12), "black"),
        (str(score), 15, (17, 30), "white"),
    ]

    # -- header highlight
    pg.draw.rect(surface, (80, 80, 80), [10, 20, 50, 20])

    # -- options
    for txt, fs, pos, fcol in options:
        font = pg.font.Font(font_name, fs)
        if txt != CAPTION:
            font.set_bold(True)

        surf = font.render(txt, True, pg.Color(fcol) if isinstance(fcol, str) else fcol)
        rect = surf.get_rect()
        rect.center = pos

        surface.blit(surf, rect)

def add_ground(space):
    w, h = SIZE[0], 20
    shape = pm.Poly.create_box(space.static_body, size=(w, h))
    shape.body.position  = (w/2, SIZE[1]+h/2)
    shape.collision_type = COLLISION_MAP.get("GroundType")
    space.add(shape)

def setup_collisions(space, blocks, bird):

    def bird_ground_solve(arbiter, space, data):
        bird.deactivate()
        blocks.deactivate()
        post_gameover()
        return True

    bghandler = space.add_collision_handler(
            COLLISION_MAP.get("BirdType"),
            COLLISION_MAP.get("GroundType")
        )
    bghandler.begin = bird_ground_solve

    def bird_block_solve(arbiter, space, data):
        bird.deactivate()
        blocks.deactivate()
        post_gameover()
        return True

    bbhandler = space.add_collision_handler(
            COLLISION_MAP.get("BirdType"),
            COLLISION_MAP.get("BlockType")
        )
    bbhandler.begin = bird_block_solve

class Bird:

    def __init__(self, size, pos, space):
        self.pos   = pos
        self.size  = size

        self.body = pm.Body(1, 1)
        self.body.position = pos

        self.shape = pm.Circle(self.body, size/2)
        self.shape.collision_type = COLLISION_MAP.get("BirdType")
        self.shape.filter = pm.ShapeFilter()
        space.add(self.body, self.shape)

        self.flap_strength = 50

    def flap(self):
        vx, vy = self.body.velocity
        self.body.velocity = (vx, -self.flap_strength)

    def deactivate(self):
        self.flap_strength = 0

    def reset(self):
        self.body.position = self.pos
        self.flap_strength = 50

    def draw(self, surface):
        r = int(self.shape.radius)
        px, py = tuple(map(int, self.body.position))

        pg.draw.circle(surface, pg.Color("yellow"), (px, py), r)
        pg.draw.rect(surface, pg.Color("black"), [px, py-(r/4), r, r/2])

    def event(self, ev):
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_SPACE:
                self.flap()

    def update(self, dt):
        pass

class Blocks:

    def __init__(self, width = 30, gap = 100, space=None):
        self.width = width
        self.gap = gap
        self.speed = 20
        self.space = space

        self.goal = None
        self.goal_index = 0
        self.blocks = []
        self.spawn_time  = 0
        self.spawn_delay = 100
        self.spawn()

        self.block_image = self.make_image()
        self.active = True

    def make_image(self):
        m = 6
        w, h = self.width, SIZE[1]*2
        surf = pg.Surface((w+m, h+m)).convert_alpha()
        surf.fill((0, 0, 0, 0))

        # -- top block
        top = int(h/2) - int(self.gap/2)
        pg.draw.rect(surf, pg.Color("black"), [0, 0, w+m, top+m])
        pg.draw.rect(surf, pg.Color("green"), [m/2, m/2, w, top])

        # -- bottom block
        bot = int(h/2) + int(self.gap/2)
        pg.draw.rect(surf, pg.Color("black"), [0, bot, w+m, h+m])
        pg.draw.rect(surf, pg.Color("green"), [m/2, bot+m/2, w, h])

        return surf

    def make_block(self, pos):
        w, h   = self.width, SIZE[1]*2
        px, py = pos

        # Top Block
        tbody  = pm.Body(body_type=pm.Body.KINEMATIC)
        tbody.position  = (px, py-((h/2) + (self.gap/2)))

        tshape = pm.Poly.create_box(tbody, size=(w,h))
        tshape.collision_type = COLLISION_MAP.get("BlockType")
        self.space.add(tbody, tshape)

        # Bottom Block
        bbody = pm.Body(body_type=pm.Body.KINEMATIC)
        bbody.position  = (px, py+((h/2) + (self.gap/2)))

        bshape = pm.Poly.create_box(bbody, size=(w,h))
        bshape.collision_type = COLLISION_MAP.get("BlockType")
        self.space.add(bbody, bshape)

        for b in [bbody, tbody]:
            b.velocity = (-self.speed, 0)
        self.blocks.append([bshape, tshape])

    def make_goal(self):
        mean_pos = lambda s: (s[0].body.position+s[1].body.position)/2
        pos = mean_pos(self.blocks[self.goal_index])

        return pg.Rect(pos.x+self.width/2, pos.y-self.gap/2, 25, self.gap)

    def deactivate(self):
        self.active = False
        for shape in [s for block in self.blocks for s in block]:
            shape.body.velocity = (0, 0)

    def reset(self):
        for shape in [s for b in self.blocks for s in b]:
            if shape.body in self.space.bodies:
                self.space.remove(shape.body, shape)

        self.goal = None
        self.goal_index = 0
        self.spawn_time = 0
        self.blocks.clear()
        self.spawn()
        self.active = True

    def draw_block(self, surface, pos):
        img = self.block_image.copy()
        rect = img.get_rect(center=pos)
        surface.blit(img, rect)

    def spawn(self):
        rand_y = random.randrange(self.gap, SIZE[1] - self.gap)
        self.make_block((500, rand_y))

    def draw(self, surface):
        # if self.goal:
        #     pg.draw.rect(surface, pg.Color("red"), self.goal, 2)
        for bblock, tblock in self.blocks:
            p = ((bblock.body.position + tblock.body.position)/2)
            self.draw_block(surface, (p.x, p.y))

    def update(self, dt, bird):
        if not self.active:
            return

        # Spawn block
        self.spawn_time += 1
        if self.spawn_time == self.spawn_delay:
            self.spawn()
            self.spawn_time = 0

        # Update goal
        self.goal = self.make_goal()
        if self.goal.collidepoint(bird.body.position):
            self.goal_index += 1
            post_score()

        # remove blocks out of view
        mean_pos = lambda s: (s[0].body.position+s[1].body.position)/2
        for shape in [s for b in self.blocks for s in b]:
            if shape.body.position.x < 0:
                if shape.body in self.space.bodies:
                    self.space.remove(shape.body, shape)

        for b in self.blocks:
            if mean_pos(b).x < 0:
                self.blocks.remove(b)
                self.goal_index -= 1
                break

if __name__ == '__main__':
    main()