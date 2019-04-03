import pyglet as pg
import pymunk as pm
from resources import Resources
from core.physics import PhysicsWorld
from core.utils import image_set_size

class Map(object):
    """ Create map from level data """

    sprites = []
    node_size = (100, 100)
    def __init__(self, data):
        super(Map, self).__init__()
        self.data = [r for r in data if '#' in r]
        self.batch = pg.graphics.Batch()
        self.generate()

    def generate(self):
        bg = pg.graphics.OrderedGroup(0)
        fg = pg.graphics.OrderedGroup(1)

        wall_img = Resources.instance.sprite('wall')
        image_set_size(wall_img, *self.node_size)
        floor_img = Resources.instance.sprite('floor')
        image_set_size(floor_img, *self.node_size)

        self.sprites.clear()
        nsx, nsy = self.node_size
        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                offx, offy = x * nsx, y * nsy
                # -- create floor tiles
                if data == " ":
                    sp = pg.sprite.Sprite(floor_img, x=offx, y=offy, batch=self.batch, group=bg)
                    self.sprites.append(sp)

                # -- create walls
                if data == "#":
                    sp = pg.sprite.Sprite(wall_img, x=offx, y=offy, batch=self.batch, group=fg)
                    self.sprites.append(sp)

                    # -- add collision box
                    world = PhysicsWorld.instance
                    wall = pm.Poly.create_box(world.space.static_body, size=self.node_size)
                    wall.body.position = (offx + nsx/2, offy + nsy/2)
                    world.add(wall)

    def on_draw(self):
        self.batch.draw()

    def _get_size(self):
        nx, ny = self.node_size
        return nx * len(self.data[0]), ny * len(self.data)
    size = property(_get_size)


