import sys
import glooey
import pyglet as pg

from resources import Resources
from gui import Label, Title, Button

class SceneManager:

    # # -- singleton
    # instance = None
    # def __new__(cls, *args):
    #     if SceneManager.instance is None:
    #         SceneManager.instance = object.__new__(cls)
    #     return SceneManager.instance

    def __init__(self, window):
        pass

    def draw(self):
        pass

    def update(self, dt):
        pass

    def key_press(self, key, modifiers):
        pass

    def key_release(self, key, modifiers):
        pass

    def mouse_press(self, x, y, button, modifiers):
        pass

    def mouse_release(self, x, y, button, modifiers):
        pass

    def mouse_motion(self, x, y, dx, dy):
        pass



def main_scene():
    vbox = glooey.VBox()
    vbox.alignment = 'center'

    title = Title("Triggered")
    vbox.add(title)

    buttons = [
           Button("Play", lambda : print("Play")),
           Button("Exit", lambda : print("Exit")),
    ]
    for button in buttons:
       vbox.add(button)

    return vbox

# def init_scenes():
#     MainScene = Scene("Main")
#     MainScene.add([
#         pg.text.Label('TRIGGERED',
#                           font_name='Times New Roman',
#                           font_size=40,
#                           x=100, y=100,
#                           anchor_x='center', anchor_y='center'),
#     ])

#     return [MainScene]

    # GameScene = Scene("Game")
    # levels = LevelManager()
    # levels.add([
    #     Level("Test", Resources.instance.level("test"))
    # ])
    # GameScene.add(levels)

    # PauseScene = Scene("Pause")
    # PauseScene.add([
    #     Label("PAUSED", (400, 300), font_size=60, fg=pg.Color("Red")),

    #     Button("RESUME", (200, 50), (650, 550), font_size=40,
    #             on_clicked=lambda : SceneManager.instance.resume()),
    #     Button("QUIT", (200, 50), (150, 550), font_size=40,
    #             on_clicked=lambda : SceneManager.instance.switch("Main")),
    # ])

    # def quit_main():
    #     for scn in SceneManager.instance:
    #         if scn.name == "Game":
    #             scn.elements[-1].current().reload()
    #             break
    #     SceneManager.instance.switch("Main")

    # def retry_level():
    #     for scn in SceneManager.instance:
    #         if scn.name == "Game":
    #             scn.elements[0].current().reload()
    #             break
    #     SceneManager.instance.switch("Game")

    # def next_level():
    #     for scn in SceneManager.instance:
    #         if scn.name == "Game":
    #             lm = scn.elements[0]
    #             for l in lm:
    #                 l.reload()

    #             level = lm.next()
    #             if level:
    #                 SceneManager.instance.switch("Game")
    #             else:
    #                 SceneManager.instance.switch("GameOver")

    # FailedScene = Scene("Failed")
    # FailedScene.add([
    #     Label("FAILED", (400, 300), font_size=60, fg=pg.Color("Red")),

    #     Button("RETRY", (200, 50), (650, 550), font_size=40,
    #             on_clicked=lambda : retry_level()),
    #     Button("QUIT", (200, 50), (150, 550), font_size=40,
    #             on_clicked=lambda : quit_main()),

    # ])

    # PassedScene = Scene("Passed")
    # PassedScene.add([
    #     Label("PASSED", (400, 300), font_size=60, fg=pg.Color("Red")),

    #     Button("NEXT", (200, 50), (650, 550), font_size=40,
    #             on_clicked=lambda : next_level()),
    #     Button("QUIT", (200, 50), (150, 550), font_size=40,
    #             on_clicked=lambda : quit_main()),

    # ])

    # GameOverScene = Scene("GameOver")
    # GameOverScene.add([
    #     Label("GAME OVER", (400, 300), font_size=60, fg=pg.Color("Red")),

    #     Button("QUIT", (200, 50), (150, 550), font_size=40,
    #             on_clicked=lambda : SceneManager.instance.switch("Main")),
    # ])

    # return [MainScene, GameScene, PauseScene, PassedScene, FailedScene, GameOverScene]