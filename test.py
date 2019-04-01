import pymunk as pm
import pyglet as pg
from core.entity import Player, Enemy
from core.app import Application
from core.physics import PhysicsWorld
from core.object import Camera
from resources import Resources

class Test:

    def __init__(self):
        self.cam = Camera()
        self.cam.size = Application.instance.size
        sx, sy = Application.instance.size
        self.cam.bounds = [0, 0, sx, sy]
        Application.instance.process(self.cam)

        self.player = Player(position=(250, 300), speed=200)
        Application.instance.process(self.player)

        en = Enemy(position=(100, 100))
        Application.instance.process(en)

        walls = [
            # position -- size
            [(0 , sy/2), (10, sy)], # Left
            [(sx, sy/2), (10, sy)], # Right
            [(sx/2 ,sy), (sx, 10)], # Top
            [(sx/2 , 0), (sx, 10)], # Left
        ]
        for wall in walls:
            pos, size = wall
            space = PhysicsWorld.instance.space
            shape = pm.Poly.create_box(space.static_body, size=size)
            shape.body.position = pos
            PhysicsWorld.instance.add(shape)

    def on_update(self, dt):
        self.cam.follow(self.player.position)

    def on_draw(self):
        Application.instance.clear()
        PhysicsWorld.instance.debug_draw()


def main():
    app = Application((500, 600), "Test Application")
    res = Resources()
    app.process(PhysicsWorld())
    app.process(Test())
    app.run()

if __name__ == '__main__':
    main()

