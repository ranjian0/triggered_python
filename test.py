import pymunk as pm
import pyglet as pg

from core.scene import Scene
from resources import Resources
from core.app import Application
from core.object import Camera, Map
from core.physics import PhysicsWorld
from core.entity import Player, Enemy

def game_scene():
    level = Resources.instance.level('level_1')

    game = Scene("game")
    game.add("camera", Camera())
    game.add("map", Map(level.map))
    game.add("player", Player(position=(250, 300), speed=200))
    game.add("enemy", Enemy(position=(200, 100)))

    game.camera.bounds = (0, 0, *game.map.size)
    game.camera.track(game.player)
    return game

def main():
    app = Application((1000, 600), "Test Application")
    res = Resources()

    app.process(PhysicsWorld())
    app.process(game_scene())
    app.run()

if __name__ == '__main__':
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)
    pg.gl.glEnable(pg.gl.GL_BLEND)
    main()

