import pickle
from enum import Enum
from pyglet.window import key

from .map       import Map
from .enemy     import Enemy
from .player    import HUD, Player
from .physics   import Physics
from .resource  import Resources
# from .gui       import InfoPanel
from .core      import (
    EventType,
    draw_path,
    draw_point,
    get_window,
    setup_collisions)

class LevelStatus(Enum):
    RUNNING = 1
    FAILED  = 2
    PASSED  = 3

class Level:

    def __init__(self, name, resource_name):
        self.name = name
        self.file = Resources.instance.get_path(resource_name)
        self.data = Resources.instance.level(resource_name)

        self.phy = Physics()
        self.map = None
        self.agents = []
        self.status = LevelStatus.RUNNING

    def remove(self, obj):
        if isinstance(obj, (Player, Enemy)):
            self.agents.remove(obj)

    def save(self):
        if self.data:
            f = open(self.file, 'wb')
            pickle.dump(self.data, f)

    def reload(self):
        if not self.data: return
        self.agents.clear()
        self.phy.clear()

        # -- create HUD and Map
        self.hud = HUD()
        self.map = Map(self.data.map, physics=self.phy)

        # -- add player
        player = Player(position=self.data.player, size=(50, 50),
            image=Resources.instance.sprite("hitman1_gun"), map=self.map, physics=self.phy)
        self.agents.append(player)
        self.hud.add(player.healthbar)
        self.hud.add(player.ammobar)
        get_window().push_handlers(player)

        # -- add enemies
        for idx, point in enumerate(self.data.enemies):
            # -- get waypoints
            path = self.data.waypoints[idx]
            reversed_midpath = path[::-1][1:-1]

            e = Enemy(point, (50, 50), Resources.instance.sprite("robot1_gun"),
                path + reversed_midpath, COLLISION_MAP.get("EnemyType") + idx, self.phy)
            Enemy.COL_TYPES.append(COLLISION_MAP.get("EnemyType") + idx)

            if DEBUG:
                e.debug_data = (path, random_color())
            e.set_map(self.map)
            self.agents.append(e)

        # -- register collision types
        setup_collisions(self.phy.space)

        # -- create infopanel
        self.infopanel = InfoPanel(self.name, self.data.objectives, self.map, self.agents)
        self.show_info = False

    def get_player(self):
        for ag in self.agents:
            if isinstance(ag, Player):
                return ag
        return None

    def get_enemies(self):
        return [e for e in self.agents if isinstance(e, Enemy)]

    def draw(self):
        if not self.data: return

        self.map.draw()
        for agent in self.agents:
            agent.draw()
        self.hud.draw()

        if self.show_info:
            self.infopanel.draw()

        if DEBUG:
            self.phy.debug_draw()
            for agent in self.agents:
                if isinstance(agent, Enemy):
                    path, color = agent.debug_data
                    draw_point(agent.pos, color, 10)
                    draw_path(path, color)

    def update(self, dt):
        if not self.data: return
        self.phy.update(dt)

        for agent in self.agents:
            agent.update(dt)

        # -- change level status
        if self.get_player():
            self.status = LevelStatus.FAILED

        if len(self.get_enemies()) == 0:
            self.status = LevelStatus.PASSED

        if self.show_info:
            self.infopanel.update(dt)

    def event(self, _type, *args, **kwargs):
        if not self.data: return

        self.infopanel.event(_type, *args, **kwargs)
        for agent in self.agents:
            if hasattr(agent, 'event'):
                agent.event(_type, *args, **kwargs)

        if _type in (EventType.KEY_DOWN, EventType.KEY_UP):
            symbol = args[0]
            if symbol == key.TAB:
                self.show_info = True if (_type == EventType.KEY_DOWN) else False

class LevelManager:

    # -- singleton
    instance = None
    def __new__(cls):
        if LevelManager.instance is None:
            LevelManager.instance = object.__new__(cls)
        return LevelManager.instance

    def __init__(self):
        self.levels = []
        self.index = 0

        self.current = None
        self.completed = False

    def load(self):
        self.current = self.levels[self.index]
        self.current.reload()

    def add(self, levels):
        if isinstance(levels, list):
            self.levels.extend(levels)
        else:
            self.levels.append(levels)

    def next(self):
        self.completed = self.index == len(self.levels) - 1
        if not self.completed:
            self.index += 1
            return self.levels[self.index]
        return None

    def set(self, name):
        for idx, level in enumerate(self.levels):
            if level.name == name:
                self.index = idx
                break

    def __iter__(self):
        for l in self.levels:
            yield l

    def draw(self):
        if self.current:
            self.current.draw()

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def event(self, *args, **kwargs):
        if self.current:
            self.current.event(*args, **kwargs)

def get_current_level():
    return LevelManager.instance.current
