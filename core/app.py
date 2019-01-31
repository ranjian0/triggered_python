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

import operator
import pyglet as pg
from .event import Signal, EventType

class Application(object):
    """ Base Application """
    def __init__(self, size, name, resizable=False):
        super(Application, self).__init__()
        self.size = size
        self.name = name
        self.resizable = resizable

        self.window = pg.window.Window(*size, resizable=resizable)
        self.window.set_minimum_size(*size)
        self.window.set_caption(name)

        self.window.push_handlers(on_draw=self.clear)

    def clear(self):
        self.window.clear()

    def run(self):
        pg.app.run()

    def process(self, obj):
        if hasattr(obj, 'update'):
            pg.clock.schedule_interval(obj.update, 1/60)
        if hasattr(obj, 'event'):
            for ev in EventType:
                name = 'on_' + ev.name.lower()
                func = lambda *args : obj.event(ev, *args)
                try:
                    self.window.push_handlers(**{name:func})
                except Exception:
                    pass

        for event in self.window.event_types:
            if hasattr(obj, event):
                self.window.push_handlers(getattr(obj, event))
