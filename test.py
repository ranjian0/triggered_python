import pymunk as pm
import pyglet as pg
from core.scene import Scene
from core.object import Camera
from core.app import Application
from core.entity import Player, Enemy
from core.physics import PhysicsWorld
from resources import Resources

class Test:

    def __init__(self):
        self.scene = Scene()
        self.scene.add("camera", Camera(size=Application.instance.size))
        self.scene.add("player", Player(position=(250, 300), speed=200))
        self.scene.add("enemy", Enemy(position=(200, 100)))
        Application.instance.process(self.scene)

    def on_update(self, dt):
        self.scene.get('camera').follow(
            self.scene.get('player').position)

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
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)
    pg.gl.glEnable(pg.gl.GL_BLEND)
    main()

