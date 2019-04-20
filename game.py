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
from core.gui import (
    Label,
    Frame,
    HLayout,
    VLayout,
    TextButton,
    )

class Game:
    """ Class to manage all game states

    BEWARE::
        - of closures
        - of nested classes
        - of singletons everywhere
        - of infinite callbacks
        - of duplicate code
        - of excessive OOP
        - of terrible dragons that lie ahead

    P.S :: I KNOW, DON'T CARE!!
    """

    class Manager:
        """ Handle common events for all game scenes """
        def __init__(self, game):
            self.game = game

        def on_key_press(self, symbol, mod):
            if symbol == pg.window.key.SPACE:
                self.game._switch_scene("game")

            if symbol == pg.window.key.ESCAPE:
                scenes = ["game", "pause"]
                if self.game.current.name in scenes:
                    scenes.remove(self.game.current.name)
                    self.game._switch_scene(scenes[-1])

            if symbol == pg.window.key.N:
                self.game.game.next_level()

            if symbol == pg.window.key.Q:
                if mod & pg.window.key.MOD_CTRL:
                    pg.app.exit()

    def __init__(self):
        self.scenes = []
        self.current = None

        self.game = self._create_game()
        self.game_scene = self.game.scene()
        self.main_scene = self._create_main_scene()
        self.pause_scene = self._create_pause_scene()

        # -- initialize
        self.current = self.main_scene
        Application.process(Game.Manager(self))
        Application.process(self.current)

    def _create_game(self):
        """ Create game scene with levels """
        current_level = 0
        levels = Resources.instance.levels()

        def dummy():
            pass

        def _get_scene():
            level = list(levels.values())[current_level]

            game = Scene("game")
            game.add("physics", PhysicsWorld())
            game.add("camera",  Camera())
            game.add("map",     Map(level.map))
            game.add("player",  Player(position=level.player))
            game.add("enemy",   EnemyCollection(level.enemies, level.waypoints))

            # -- setup camera
            game.camera.bounds = (0, 0, *game.map.size)
            game.camera.track(game.player)
            self.scenes.append(game)
            return game

        def _next_level():
            nonlocal current_level
            if current_level < len(levels.values()):
                current_level += 1

                self.scenes.remove(self.current)
                Application.remove(self.current)

                self.current = _get_scene()
                self.game_scene = self.current

                Application.process(self.current)
                self.scenes.append(self.current)

        dummy.scene = _get_scene
        dummy.next_level = _next_level
        return dummy

    def _create_main_scene(self):
        w, h = Application.instance.size
        gui = Frame()
        fs = 24

        # Main Layout
        layout = VLayout()
        layout += (
            # -- title text
            HLayout(
                Label("TRIGGERED", font_size=42)
            ),

            # -- buttons
            VLayout(
                TextButton("Play", font_size=fs),
                TextButton("Settings", font_size=fs),
                TextButton("Exit", font_size=fs)
            )
        )
        gui += layout

        # -- Create the scene
        main = Scene("main")
        main.add("gui", gui)
        self.scenes.append(main)
        return main

    def _create_pause_scene(self):
        pause = Scene("pause")
        self.scenes.append(pause)
        return pause

    def _switch_scene(self, name):
        already_active = self.current.name == name
        does_not_exist = name not in [sc.name for sc in self.scenes]
        if already_active or does_not_exist:
            return

        Application.remove(self.current)
        self.current = next(filter(lambda sc:sc.name==name, self.scenes))
        Application.process(self.current)


def main():
    res = Resources()
    app = Application((1366, 680), "Triggered")
    game = Game()
    app.run()

if __name__ == '__main__':
    main()