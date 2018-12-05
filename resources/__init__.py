import os
import pickle
import pyglet as pg

from collections import namedtuple

Resource  = namedtuple("Resource", "name data")
LevelData = namedtuple("LevelData",
            ["map",
             "player",
             "enemies",
             "waypoints",
             "lights",
             "objectives"])


class Resources:

    # -- singleton
    instance = None
    def __new__(cls):
        if Resources.instance is None:
            Resources.instance = object.__new__(cls)
        return Resources.instance

    def __init__(self):
        self.root = os.path.dirname(os.path.realpath(__file__))
        pg.resource.path = [
            os.path.dirname(os.path.realpath(__file__))
        ]
        pg.resource.reindex()

        abspath = os.path.abspath
        self._sprites = abspath(os.path.join(self.root, "sprites"))
        self._sounds  = abspath(os.path.join(self.root, "sounds"))
        self._levels  = abspath(os.path.join(self.root, "levels"))

        self._data = defaultdict(list)
        self._load()

    def get_path(self, name):
        # -- determine the full path of a resource called name
        for sprite in os.listdir(self._sprites):
            n = sprite.split('.')[0]
            if n == name:
                return os.path.join(self._sprites, sprite)

        for sound in os.listdir(self._sounds):
            n = sound.split('.')[0]
            if n == name:
                return os.path.join(self._sounds, sound)

        for level in os.listdir(self._levels):
            n = level.split('.')[0]
            if n == name:
                return os.path.join(self._levels, level)
        return None

    def sprite(self, name):
        for res in self._data['sprites']:
            if res.name == name:
                return res.data
        return None

    def sound(self, name):
        for res in self._data['sounds']:
            if res.name == name:
                return res.data
        return None

    def level(self, name):
        for res in self._data['levels']:
            if res.name == name:
                return self._parse_level(res.data)
        else:
            # -- filename does not exit, create level file
            fn = name + '.level'
            path = os.path.join(self._levels, fn)
            with open(path, 'wb') as _:
                pass

            # -- create level resource
            pg.resource.reindex()
            lvl = pg.resource.file('levels/' + fn)

            # -- add resource to database
            self._data['levels'].append(Resource(name,lvl))
            print(f"Created new level {name}")
            return self._parse_level(lvl)

    def levels(self):
        level_data = {}
        for res in self._data['levels']:
            level_data[res.data.name] = self._parse_level(res.data)
        return level_data

    def _load(self):

        # -- load sprites
        for sprite in os.listdir(self._sprites):
            img = pg.resource.image('sprites/' + sprite)
            fn = os.path.basename(sprite.split('.')[0])
            self._data['sprites'].append(Resource(fn,img))

        # -- load sounds
        for sound in os.listdir(self._sounds):
            snd = pg.resource.media('sounds/' + sound)
            fn = os.path.basename(sound.split('.')[0])
            self._data['sounds'].append(Resource(fn,snd))

        # -- load levels
        for level in os.listdir(self._levels):
            lvl = pg.resource.file('levels/' + level)
            fn = os.path.basename(level.split('.')[0])
            self._data['levels'].append(Resource(fn,lvl))

    def _parse_level(self, file):
        try:
            return pickle.load(file)
        except EOFError as e:
            # -- file object already consumed
            try:
                return pickle.load(open(file.name, 'rb'))
            except EOFError as e:
                # -- file is actually empty, return default data
                return LevelData([[]], (100, 100), [], [], [], [])

