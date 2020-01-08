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

import types
import pyglet as pg

from core.scene import Scene
from resources import Resources
from core.app import Application
from core.object import Camera, Map
from core.physics import PhysicsWorld
from core.entity import Player, EnemyCollection
from core.gui import Label, Frame, HLayout, VLayout, TextButton


class Game(Application):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scenes = []
        self.current_scene = None

        self.game = self._create_game()
        self.game_scene = self.game.scene()
        self.main_scene = self._create_main_scene()
        self.pause_scene = self._create_pause_scene()
        self.settings_scene = self._create_settings_scene()

        # -- initialize
        self.current_scene = self.main_scene
        self.process(Game.EventManager(self))
        self.process(self.current_scene)

    def _create_game(self):
        """ Create game scene with levels """
        current_level = 0
        levels = Resources.instance.levels()

        def _get_scene():
            level = list(levels.values())[current_level]

            game = Scene("game")
            game.add("physics", PhysicsWorld())
            game.add("camera", Camera())
            game.add("map", Map(level.map))
            game.add("player", Player(position=level.player))
            game.add("enemy", EnemyCollection(level.enemies, level.waypoints))

            # -- setup camera
            game.camera.bounds = (0, 0, *game.map.size)
            game.camera.track(game.player)
            self.scenes.append(game)
            return game

        def _next_level():
            nonlocal current_level
            if current_level < len(levels.values()) - 1:
                current_level += 1

                self.scenes.remove(self.current_scene)
                self.remove(self.current_scene)

                self.current_scene = _get_scene()
                self.game_scene = self.current_scene

                self.process(self.current_scene)
                self.scenes.append(self.current_scene)

        def _previous_level():
            nonlocal current_level
            if current_level > 0:
                current_level -= 1

                self.scenes.remove(self.current_scene)
                self.remove(self.current_scene)

                self.current_scene = _get_scene()
                self.game_scene = self.current_scene

                self.process(self.current_scene)
                self.scenes.append(self.current_scene)

        game = types.SimpleNamespace(
            scene=_get_scene, next_level=_next_level, previous_level=_previous_level
        )
        return game

    def _create_main_scene(self):
        gui = Frame()

        # Main Layout
        layout = VLayout()
        layout += (
            # -- title text
            HLayout(Label("TRIGGERED", font_size=42)),
            # -- buttons
            VLayout(
                TextButton(
                    "Play", font_size=24, callback=lambda: self._switch_scene("game")
                ),
                TextButton(
                    "Settings",
                    font_size=24,
                    callback=lambda: self._switch_scene("settings"),
                ),
                TextButton("Exit", font_size=24, callback=lambda: pg.app.exit()),
            ),
        )
        gui += layout

        # -- Create the scene
        main = Scene("main")
        main.add("gui", gui)
        self.scenes.append(main)
        return main

    def _create_pause_scene(self):
        gui = Frame()

        # Main Layout
        layout = VLayout()
        layout += (
            # -- title text
            HLayout(Label("PAUSE", font_size=42)),
            # -- buttons
            HLayout(
                TextButton(
                    "Continue",
                    font_size=24,
                    callback=lambda: self._switch_scene("game"),
                ),
                TextButton(
                    "Main", font_size=24, callback=lambda: self._switch_scene("main")
                ),
            ),
        )
        gui += layout

        pause = Scene("pause")
        pause.add("pause_gui", gui)
        self.scenes.append(pause)
        return pause

    def _create_settings_scene(self):
        gui = Frame()

        # Main Layout
        layout = VLayout()
        layout += (
            # -- title text
            HLayout(Label("SETTINGS", font_size=42)),
            # -- buttons
            HLayout(
                TextButton(
                    "Back to MainMenu",
                    font_size=24,
                    callback=lambda: self._switch_scene("main"),
                ),
                TextButton("Exit", font_size=24, callback=lambda: pg.app.exit()),
            ),
        )
        gui += layout

        settings = Scene("settings")
        settings.add("settings_gui", gui)
        self.scenes.append(settings)
        return settings

    def _switch_scene(self, name):
        already_active = self.current_scene.name == name
        does_not_exist = name not in [sc.name for sc in self.scenes]
        if already_active or does_not_exist:
            return

        self.remove(self.current_scene)
        self.current_scene = next(filter(lambda sc: sc.name == name, self.scenes))
        self.process(self.current_scene)

    class EventManager:
        """ Handle common events for all game scenes """

        def __init__(self, base):
            self.base = base

        def on_key_press(self, symbol, mod):
            base = self.base
            game = self.base.game

            if symbol == pg.window.key.SPACE:
                if base.current_scene.name == "main":
                    base._switch_scene("game")
                else:
                    base._switch_scene("main")

            if symbol == pg.window.key.ESCAPE:
                scenes = ["game", "pause"]
                if base.current_scene.name in scenes:
                    idx = scenes.index(base.current_scene.name)
                    base._switch_scene(scenes[1 - idx])

            if symbol == pg.window.key.N:
                game.next_level()

            if symbol == pg.window.key.P:
                game.previous_level()

            if symbol == pg.window.key.Q:
                if mod & pg.window.key.MOD_CTRL:
                    pg.app.exit()


def main():
    Resources()
    game = Game((1366, 680), "Triggered")
    game.run()


if __name__ == "__main__":
    main()
