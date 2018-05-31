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
    "HitEvent" : pg.USEREVENT + 1
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

    add_ground(space)
    setup_collisions(space, score)

    while True:

        # -- Events
        for event in pg.event.get():

            QUIT_COND = [
                event.type == pg.QUIT,
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE,]
                # event.type == EVENT_MAP.get("HitEvent")]

            if any(QUIT_COND):
                pg.quit()
                sys.exit()


            bird.event(event)

        # -- Draw
        screen.fill(BACKGROUND)
        bird.draw(screen)
        blocks.draw(screen)

        # options = putils.DrawOptions(screen)
        # space.debug_draw(options)

        pg.display.flip()

        # -- Update
        dt = clock.tick(FPS) / 1000.0
        for _ in range(PHYSICS_STEP):
            space.step(0.1 / PHYSICS_STEP)
        bird.update(dt)
        blocks.update(dt)

def post_hit():
    hit_event = pg.event.Event(EVENT_MAP.get("HitEvent"))
    pg.event.post(hit_event)

def add_ground(space):
    w, h = SIZE[0], 20
    shape = pm.Poly.create_box(space.static_body, size=(w, h))
    shape.body.position  = (w/2, SIZE[1]+h/2)
    shape.collision_type = COLLISION_MAP.get("GroundType")
    space.add(shape)

def setup_collisions(space, score):

    def bird_ground_solve(arbiter, space, data):
        post_hit()
        return True

    bghandler = space.add_collision_handler(
            COLLISION_MAP.get("BirdType"),
            COLLISION_MAP.get("GroundType")
        )
    bghandler.begin = bird_ground_solve

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

    def __init__(self, width = 30, gap = 75, space=None):
        self.width = width
        self.gap = gap
        self.speed = 10
        self.space = space

        self.blocks = []
        self.spawn_time  = 0
        self.spawn_delay = 100
        self.spawn()

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
        tbody  = pm.Body(1,1, pm.Body.KINEMATIC)
        tbody.position  = (px, py-((h/2) + (self.gap/2)))

        tshape = pm.Poly.create_box(tbody, size=(w,h))
        tshape.collision_type = COLLISION_MAP.get("BlockType")
        self.space.add(tbody, tshape)

        # Bottom Block
        bbody = pm.Body(1,1, pm.Body.KINEMATIC)
        bbody.position  = (px, py+((h/2) + (self.gap/2)))

        bshape = pm.Poly.create_box(bbody, size=(w,h))
        bshape.collision_type = COLLISION_MAP.get("BlockType")
        self.space.add(bbody, bshape)


        block = [bbody, tbody]
        for b in block:
            b.velocity = (-self.speed, 0)
        self.blocks.append([bbody, tbody])

    def draw(self, surface):
        for bblock, tblock in self.blocks:
            p = ((bblock.position + tblock.position)/2)
            self.draw_block(surface, (p.x, p.y))

    def draw_block(self, surface, pos):
        img = self.make_image()
        rect = img.get_rect(center=pos)
        surface.blit(img, rect)


    def update(self, dt):
        # Do spawn
        self.spawn_time += 1
        if self.spawn_time == self.spawn_delay:
            self.spawn()
            self.spawn_time = 0

        # # remove blocks out of view
        # for bodies in self.blocks:
        #     for body in bodies:
        #         if body.position.x + self.width < 0:
        #             self.space.remove(body)

    def spawn(self):
        rand_y = random.randrange(self.gap, SIZE[1] - self.gap)
        self.make_block((500, rand_y))


if __name__ == '__main__':
    main()