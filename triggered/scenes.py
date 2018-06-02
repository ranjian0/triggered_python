import sys
import pygame as pg

from gui import Label, Button

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
            if ev.type == pg.KEYDOWN and ev.key == pg.K_TAB:
                if self.current.name == "Game":
                    self.current.paused = True
                    self.switch("Pause")
            self.current.event(ev)


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
# GameScene.add([
#     Map()
# ])

PauseScene = Scene("Pause")
PauseScene.add([
    Label("PAUSED", (400, 300), font_size=60, fg=pg.Color("Red")),

    Button("RESUME", (200, 50), (650, 550), font_size=40,
            on_clicked=lambda : SceneManager.instance.resume()),
    Button("QUIT", (200, 50), (150, 550), font_size=40,
            on_clicked=lambda : SceneManager.instance.switch("Main")),
])

FailedScene = Scene("Failed")
FailedScene.add([
    Label("FAILED", (400, 300), font_size=60, fg=pg.Color("Red")),

    Button("RETRY", (200, 50), (650, 550), font_size=40,
            on_clicked=lambda : None),
    Button("QUIT", (200, 50), (150, 550), font_size=40,
            on_clicked=lambda : SceneManager.instance.switch("Main")),

])

PassedScene = Scene("Passed")
PassedScene.add([
    Label("PASSED", (400, 300), font_size=60, fg=pg.Color("Red")),

    Button("NEXT", (200, 50), (650, 550), font_size=40,
            on_clicked=lambda : None),
    Button("QUIT", (200, 50), (150, 550), font_size=40,
            on_clicked=lambda : None),

])

GameOverScene = Scene("GameOver")
GameOverScene.add([
    Label("GAME OVER", (400, 300), font_size=60, fg=pg.Color("Red")),

    Button("QUIT", (200, 50), (150, 550), font_size=40,
            on_clicked=lambda : None),
])