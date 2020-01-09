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

import functools
import pyglet as pg

from .utils import profile


class Application(object):
    """ Base Application """

    # -- singleton
    instance = None

    def __new__(cls, *args, **kwargs):
        if Application.instance is None:
            Application.instance = object.__new__(cls)
        return Application.instance

    def __init__(self, size, name, resizable=False):
        super(Application, self).__init__()
        self._size = size
        self._name = name
        self._resizable = resizable

        self._window = pg.window.Window(*size, resizable=resizable)
        self._window.set_minimum_size(*size)
        self._window.set_caption(name)
        self._window.maximize()
        self._window.push_handlers(on_key_press=self._skip_escape)

        # XXX A CUSTOM EVENT DISPATCHER
        # WHY:
        # Guarantees a symmetrical stack with process and remove methods

        # NOTE:
        # we push an on_draw event to the window during run, making its stack unsymmetrical

        self._events = AppEvents()
        self._window.push_handlers(
            **{ev: getattr(self._events, "do_" + ev[3:]) for ev in EVENTS}
        )

    def _clear(self):
        self._window.clear()
        pg.gl.glClearColor(0.2, 0.3, 0.3, 1)

    def _skip_escape(self, symbol, mod):
        if symbol == pg.window.key.ESCAPE:
            return True

    def _get_window(self):
        return self._window

    window = property(_get_window)

    def _get_size(self):
        self._size = self._window.get_size()
        return self._size

    def _set_size(self, val):
        self._size = val
        self._window.set_size(*val)

    size = property(_get_size, _set_size)
    w = property(lambda self: self._window.width)
    h = property(lambda self: self._window.height)

    def _get_name(self):
        return self.name

    def _set_name(self, val):
        self._name = val
        self._window.set_caption(val)

    name = property(_get_name, _set_name)

    def run(self, debug=False):
        self._window.push_handlers(on_draw=self._clear)
        pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)
        pg.gl.glEnable(pg.gl.GL_BLEND)
        with profile(debug):
            pg.app.run()

    @staticmethod
    def quit():
        pg.app.exit()

    @classmethod
    def process(cls, obj):
        self = cls.instance
        self._events.push_handlers(obj)
        if hasattr(obj, "on_update"):
            pg.clock.schedule_interval(obj.on_update, 1 / 60)

    @classmethod
    def remove(cls, obj):
        self = cls.instance
        self._events.pop_handlers()
        if hasattr(obj, "on_update"):
            pg.clock.unschedule(obj.on_update)


class AppEvents(pg.event.EventDispatcher):
    def do_draw(self):
        self.dispatch_event("on_draw")

    def do_update(self, dt):
        self.dispatch_event("on_update", dt)

    def do_resize(self, *args):
        self.dispatch_event("on_resize", *args)

    def do_key_press(self, *args):
        self.dispatch_event("on_key_press", *args)

    def do_key_release(self, *args):
        self.dispatch_event("on_key_release", *args)

    def do_mouse_press(self, *args):
        self.dispatch_event("on_mouse_press", *args)

    def do_mouse_release(self, *args):
        self.dispatch_event("on_mouse_release", *args)

    def do_mouse_drag(self, *args):
        self.dispatch_event("on_mouse_drag", *args)

    def do_mouse_motion(self, *args):
        self.dispatch_event("on_mouse_motion", *args)

    def do_mouse_scroll(self, *args):
        self.dispatch_event("on_mouse_scroll", *args)

    def do_text(self, *args):
        self.dispatch_event("on_text", *args)

    def do_text_motion(self, *args):
        self.dispatch_event("on_text_motion", *args)

    def do_text_motion_select(self, *args):
        self.dispatch_event("on_text_motion_select", *args)


EVENTS = [
    "on_key_press",
    "on_key_release",
    "on_text",
    "on_text_motion",
    "on_text_motion_select",
    "on_mouse_motion",
    "on_mouse_drag",
    "on_mouse_press",
    "on_mouse_release",
    "on_mouse_scroll",
    "on_resize",
    "on_draw",
]
for ev in EVENTS:
    AppEvents.register_event_type(ev)
