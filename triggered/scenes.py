import sys
import pygame as pg

from gui import Label, Button

from levels import (
    LevelManager,
    LevelOne)

class Scene:
    NAME      = "Scene"
    DRAWABLES = []

    def __init__(self, manager):
        self.manager = manager
        assert self.NAME != "Scene", "Scene must have unique name"

    def draw(self, surface):
        for drawable in self.DRAWABLES:
            if hasattr(drawable, 'draw'):
                drawable.draw(surface)

    def update(self, dt):
        for drawable in self.DRAWABLES:
            if hasattr(drawable, 'update'):
                drawable.update(dt)

    def event(self, ev):
        for drawable in self.DRAWABLES:
            if hasattr(drawable, 'event'):
                drawable.event(ev)

class SceneManager:

    def __init__(self):

        self.scenes      = []
        self.start_scene = None
        self.current     = None

    def add(self, scene, is_main=False):
        if is_main:
            self.start_scene = scene(self)
            self.current     = scene(self)
        self.scenes.append(scene)

    def switch(self, name):
        self.current = [scn for scn in self.scenes
                        if scn.NAME == name][-1](self)

    def draw(self, surface):
        if self.current:
            self.current.draw(surface)

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def event(self, ev):
        if self.current:
            self.current.event(ev)

class MainScene(Scene):
    NAME = "MainMenu"

    def __init__(self, manager):
        Scene.__init__(self, manager)
        self.DRAWABLES = [
            Label("TRIGGERED", (400, 50), font_size=60, fg=pg.Color("Red")),

            Button("PLAY", (200, 50), (400, 200), font_size=40,
                    on_clicked=lambda : self.manager.switch(GameScene.NAME)),

            Button("EXIT", (200, 50), (400, 270), font_size=40,
                    on_clicked=lambda : sys.exit()),

            Label("Created by Ian Karanja", (700, 580), font_size=20, fg=pg.Color("White")),
        ]

class GameScene(Scene):
    NAME = "GAME"

    def __init__(self, manager):
        Scene.__init__(self, manager)
        self.levels = LevelManager([
                        LevelOne()
                    ])

    def draw(self, surface):
        super().draw(surface)
        self.levels.get_current().draw(surface)

    def update(self, dt):
        super().update(dt)
        self.levels.get_current().update(dt)

    def event(self, event):
        super().event(event)
        self.levels.get_current().event(event)

class PauseScene(Scene):
    NAME = "Pause"

    def __init__(self, manager):
        Scene.__init__(self, manager)
        self.DRAWABLES = [
            Label("PAUSED", (400, 300), font_size=60, fg=pg.Color("Red")),

            Button("RESUME", (200, 50), (650, 550), font_size=40,
                    on_clicked=lambda : self.manager.switch(GameScene.NAME)),

            Button("QUIT", (200, 50), (150, 550), font_size=40,
                    on_clicked=lambda : self.manager.switch(MainScene.NAME)),
        ]

class LevelFailed(Scene):
    NAME = "LevelFailed"

    def __init__(self, manager):
        Scene.__init__(self, manager)
        self.DRAWABLES = [
            Label("LEVEL FAILED", (400, 300), font_size=60, fg=pg.Color("Red")),

            Button("RETRY", (200, 50), (650, 550), font_size=40,
                    on_clicked=lambda : self.manager.switch(GameScene.NAME)),

            Button("QUIT", (200, 50), (150, 550), font_size=40,
                    on_clicked=lambda : self.manager.switch(MainScene.NAME)),
        ]

class LevelPassed(Scene):
    NAME = "LevelPassed"

    def __init__(self, manager):
        Scene.__init__(self, manager)
        self.DRAWABLES = [
            Label("LEVEL PASSED", (400, 300), font_size=60, fg=pg.Color("Red")),

            # TODO : reference to LevelManager
            # Button("NEXT", (200, 50), (650, 550), font_size=40,
            #         on_clicked=lambda : LevelManager.instance.go_next()),

            Button("QUIT", (200, 50), (150, 550), font_size=40,
                    on_clicked=lambda : self.manager.switch(MainScene.NAME)),
        ]

class GameOver(Scene):
    NAME = "GameOver"

    def __init__(self, manager):
        Scene.__init__(self, manager)
        self.DRAWABLES = [
            Label("GAME OVER", (400, 300), font_size=60, fg=pg.Color("Red")),

            Button("QUIT", (200, 50), (150, 550), font_size=40,
                    on_clicked=lambda : self.manager.switch(MainScene.NAME)),
        ]

