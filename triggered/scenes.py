import sys
import pygame as pg

from resources import Resources
from gui       import Label, Button
from levels    import (
    LevelManager, Level, FAILED_EVT, PASSED_EVT)

class Scene:

    def __init__(self, name):
        self.name     = name
        self.elements = []

        self.paused = False

    def add(self, items):
        if isinstance(items, list):
            self.elements.extend(items)
        else:
            self.elements.append(items)

    def draw(self, surface):
        for elem in self.elements:
            if hasattr(elem, 'draw'):
                elem.draw(surface)

    def update(self, dt):
        if self.paused: return
        for elem in self.elements:
            if hasattr(elem, 'update'):
                elem.update(dt)

    def event(self, ev):
        if self.paused: return
        for elem in self.elements:
            if hasattr(elem, 'event'):
                elem.event(ev)

class SceneManager:

    # -- singleton
    instance = None
    def __new__(cls):
        if SceneManager.instance is None:
            SceneManager.instance = object.__new__(cls)
        return SceneManager.instance

    def __init__(self):
        self.scenes  = []
        self.current = None

    def __iter__(self):
        for scn in self.scenes:
            yield scn

    def add(self, scene, is_main=False):
        if is_main:
            self.current = scene
        self.scenes.append(scene)

    def switch(self, name):
        for scn in self.scenes:
            if scn.name == name:
                self.current = scn
                break

    def resume(self):
        self.current.paused = False
        self.switch("Game")

    def draw(self, surface):
        if self.current:
            self.current.draw(surface)

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def event(self, ev):
        if self.current:
            self.current.event(ev)
            if ev.type == pg.KEYDOWN and ev.key == pg.K_TAB:
                if self.current.name == "Game":
                    self.current.paused = True
                    self.switch("Pause")

            if ev.type == FAILED_EVT:
                self.switch("Failed")
            if ev.type == PASSED_EVT:
                self.switch("Passed")

def init_scenes():
    MainScene = Scene("Main")
    MainScene.add([
        Label("TRIGGERED", (400, 50), font_size=60, fg=pg.Color("Red")),
        Button("PLAY", (200, 50), (400, 200), font_size=40,
                on_clicked=lambda : SceneManager.instance.switch("Game")),
        Button("EXIT", (200, 50), (400, 270), font_size=40,
                on_clicked=lambda : sys.exit()),
        Label("Created by Ian Karanja", (700, 580), font_size=20, fg=pg.Color("White")),
    ])

    GameScene = Scene("Game")
    levels = LevelManager()
    levels.add([
        Level("Test", Resources.instance.level("test"))
    ])
    GameScene.add(levels)

    PauseScene = Scene("Pause")
    PauseScene.add([
        Label("PAUSED", (400, 300), font_size=60, fg=pg.Color("Red")),

        Button("RESUME", (200, 50), (650, 550), font_size=40,
                on_clicked=lambda : SceneManager.instance.resume()),
        Button("QUIT", (200, 50), (150, 550), font_size=40,
                on_clicked=lambda : SceneManager.instance.switch("Main")),
    ])

    def quit_main():
        for scn in SceneManager.instance:
            if scn.name == "Game":
                scn.elements[-1].current().reload()
                break
        SceneManager.instance.switch("Main")

    def retry_level():
        for scn in SceneManager.instance:
            if scn.name == "Game":
                scn.elements[0].current().reload()
                break
        SceneManager.instance.switch("Game")

    def next_level():
        for scn in SceneManager.instance:
            if scn.name == "Game":
                lm = scn.elements[0]
                for l in lm:
                    l.reload()

                level = lm.next()
                if level:
                    SceneManager.instance.switch("Game")
                else:
                    SceneManager.instance.switch("GameOver")

    FailedScene = Scene("Failed")
    FailedScene.add([
        Label("FAILED", (400, 300), font_size=60, fg=pg.Color("Red")),

        Button("RETRY", (200, 50), (650, 550), font_size=40,
                on_clicked=lambda : retry_level()),
        Button("QUIT", (200, 50), (150, 550), font_size=40,
                on_clicked=lambda : quit_main()),

    ])

    PassedScene = Scene("Passed")
    PassedScene.add([
        Label("PASSED", (400, 300), font_size=60, fg=pg.Color("Red")),

        Button("NEXT", (200, 50), (650, 550), font_size=40,
                on_clicked=lambda : next_level()),
        Button("QUIT", (200, 50), (150, 550), font_size=40,
                on_clicked=lambda : quit_main()),

    ])

    GameOverScene = Scene("GameOver")
    GameOverScene.add([
        Label("GAME OVER", (400, 300), font_size=60, fg=pg.Color("Red")),

        Button("QUIT", (200, 50), (150, 550), font_size=40,
                on_clicked=lambda : SceneManager.instance.switch("Main")),
    ])

    return [MainScene, GameScene, PauseScene, PassedScene, FailedScene, GameOverScene]