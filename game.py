#  Copyright 2019 Ian Karanja <karanjaichungwa@gmail.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import pymunk as pm
import pyglet as pg

from core.scene import Scene
from resources import Resources
from core.app import Application
from core.object import Camera, Map
from core.physics import PhysicsWorld
from core.entity import Player, EnemyCollection

def game_scene():
    level = Resources.instance.level('level_1')

    game = Scene("game")
    game.add("camera",  Camera())
    game.add("map",     Map(level.map))
    game.add("player",  Player(position=(250, 300), speed=200))
    game.add("enemy",   EnemyCollection(level.enemies, level.waypoints))

    # -- setup camera
    game.camera.bounds = (0, 0, *game.map.size)
    game.camera.track(game.player)
    return game

def main():
    app = Application((1366, 680), "Test Application")
    res = Resources()

    app.process(PhysicsWorld())
    app.process(game_scene())
    app.run()

if __name__ == '__main__':
    main()