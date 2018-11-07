import os
import pickle
import pyglet as pg

from collections import namedtuple, defaultdict

Resource  = namedtuple("Resource", "name data")

class Resources:

    # -- singleton
    instance = None
    def __new__(cls):
        if Resources.instance is None:
            Resources.instance = object.__new__(cls)
        return Resources.instance

    def __init__(self, root_dir="res"):
        self.root = root_dir
        pg.resource.path = [os.path.abspath(root_dir)]
        pg.resource.reindex()

        abspath = os.path.abspath
        self._sprites = abspath(os.path.join(root_dir, "sprites"))
        self._sounds  = abspath(os.path.join(root_dir, "sounds"))
        self._levels  = abspath(os.path.join(root_dir, "levels"))

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
            with open(path, 'w') as _:
                pass

            # -- create level resource
            pg.resource.reindex()
            lvl = pg.resource.file('levels/' + fn, 'r')

            # -- add resource to database
            self._data['levels'].append(Resource(name,lvl))
            print(f"Created new level {name}")
            return self._parse_level(lvl)

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
        except EOFError:
            return None
