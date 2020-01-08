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

import operator as op


class Collection:
    """ Base class to manage a collection of objects """

    def __init__(self, object_type):
        self._class = object_type
        self._items = []

    def add(self, *args, **kwargs):
        """ Add a single object of type self._class to the collection """
        obj = self._class(*args, **kwargs)
        self._items.append(obj)

    def add_many(self, count, *args, **kwargs):
        """ Add count objects of type self._class to the collection """
        for idx in range(count):
            kw = {k: v[idx] for k, v in kwargs.items()}
            arg = () if not len(args) else args[idx]
            self.add(*arg, **kw)

    def __iter__(self):
        return iter(self._items)

    def _iter_call_meth(self, method, *args, **kwargs):
        """ Call meth for all objects """
        for obj in self:
            if hasattr(obj, method):
                f = op.methodcaller(method, *args, **kwargs)
                f(obj)

    # XXX Event handlers
    def on_draw(self):
        self._iter_call_meth("on_draw")

    def on_draw_first(self):
        self._iter_call_meth("on_draw_first")

    def on_draw_last(self):
        self._iter_call_meth("on_draw_last")

    def on_update(self, dt):
        self._iter_call_meth("on_update", dt)

        # -- remove destroyed items from the collection
        self._items = [
            item
            for item in self
            if (hasattr(item, "destroyed") and not item.destroyed)
            or not hasattr(item, "destroyed")
        ]

    def on_resize(self, *args):
        self._iter_call_meth("on_resize", *args)

    def on_key_press(self, *args):
        self._iter_call_meth("on_key_press", *args)

    def on_key_release(self, *args):
        self._iter_call_meth("on_key_release", *args)

    def on_mouse_press(self, *args):
        self._iter_call_meth("on_mouse_press", *args)

    def on_mouse_release(self, *args):
        self._iter_call_meth("on_mouse_release", *args)

    def on_mouse_drag(self, *args):
        self._iter_call_meth("on_mouse_drag", *args)

    def on_mouse_motion(self, *args):
        self._iter_call_meth("on_mouse_motion", *args)

    def on_mouse_scroll(self, *args):
        self._iter_call_meth("on_mouse_scroll", *args)

    def on_text(self, *args):
        self._iter_call_meth("on_text", *args)

    def on_text_motion(self, *args):
        self._iter_call_meth("on_text_motion", *args)

    def on_text_motion_select(self, *args):
        self._iter_call_meth("on_text_motion_select", *args)
