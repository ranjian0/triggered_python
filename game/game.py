import enum
from pyglet.window import key

from .settings  import LEVELS
from .signal    import connect
from .resource  import Resources
from .core      import EventType
from .editor    import LevelEditor
from .gui       import MainMenu, PauseMenu
from .level     import Level, LevelManager


class GameState(enum.Enum):
    MAINMENU = 1
    RUNNING  = 2
    PAUSED   = 3
    EDITOR   = 4

class Game:

    def __init__(self):
        self.res = Resources()
        self.state = GameState.MAINMENU

        self.editor = LevelEditor()
        self.manager = LevelManager()
        self.manager.add([
            Level(name, file) for name, file in LEVELS
        ])

        self.mainmenu = MainMenu()
        self.pausemenu = PauseMenu()

        # global signals
        connect("start_game", self, "start")    # -> MainMenu

    def start(self, level_name):
        self.manager.set(level_name)
        self.manager.load()
        self.state = GameState.RUNNING

    def pause(self):
        self.state = GameState.PAUSED

    def draw(self):
        if self.state == GameState.MAINMENU:
            self.mainmenu.draw()
        elif self.state == GameState.PAUSED:
            self.pausemenu.draw()
        elif self.state == GameState.RUNNING:
            self.manager.draw()
        elif self.state == GameState.EDITOR:
            self.editor.draw()

    def event(self, _type, *args, **kwargs):

        if self.state == GameState.MAINMENU:
            self.mainmenu.event(_type, *args, **kwargs)

        elif self.state == GameState.PAUSED:
            self.pausemenu.event(_type, *args, **kwargs)

            if _type == EventType.KEY_DOWN:
                symbol, mod = args

                if symbol == key.P:
                    self.state = GameState.RUNNING

        elif self.state == GameState.RUNNING:
            self.manager.event(_type, *args, **kwargs)

            if _type == EventType.KEY_DOWN:
                symbol, mod = args

                if symbol == key.P:
                    self.pausemenu.reload()
                    self.state = GameState.PAUSED

                if symbol == key.E and mod & key.MOD_CTRL:
                    self.editor.load(self.manager.current)
                    self.state = GameState.EDITOR

        elif self.state == GameState.EDITOR:
            self.editor.event(_type, *args, **kwargs)

            if _type == EventType.KEY_DOWN:
                symbol, mod = args

                if symbol == key.E and mod & key.MOD_CTRL:
                    self.editor.save()
                    self.state = GameState.RUNNING

    def update(self, dt):
        if self.state == GameState.MAINMENU:
            self.mainmenu.update(dt)
        elif self.state == GameState.RUNNING:
            self.manager.update(dt)
        elif self.state == GameState.PAUSED:
            self.pausemenu.update(dt)
        elif self.state == GameState.EDITOR:
            self.editor.update(dt)
