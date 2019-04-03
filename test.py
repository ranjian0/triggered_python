import pymunk as pm
import pyglet as pg
from core.scene import Scene
from core.object import Camera, Map
from core.app import Application
from core.entity import Player, Enemy
from core.physics import PhysicsWorld
from resources import Resources

def test():
    level = Resources.instance.level('level_1')

    scene = Scene()
    scene.add("camera", Camera())
    scene.add("map", Map(level.map))
    scene.add("player", Player(position=(250, 300), speed=200))
    scene.add("enemy", Enemy(position=(200, 100)))
    Application.process(scene)

    scene.camera.bounds = (0, 0, *scene.map.size)
    scene.camera.track(scene.player)


def main():
    app = Application((1000, 600), "Test Application")
    res = Resources()
    app.process(PhysicsWorld())
    test()
    app.run()

if __name__ == '__main__':
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)
    pg.gl.glEnable(pg.gl.GL_BLEND)
    main()

