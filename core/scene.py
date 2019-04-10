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

class Scene(object):
    """ Container object to manage other objects """

    def __init__(self, name):
        super(Scene, self).__init__()
        self.name = name
        self.objects = dict()

    def add(self, name, obj):
        if name in self.objects.keys():
            raise ValueError(f"Object with name '{name}' already exists!")
        self.objects[name] = obj

    def add_many(self, **kwargs):
        for key, val in kwargs.items():
            self.add(key, val)

    def __getattr__(self, name):
        return self.objects.get(name, None)

    def __iter__(self):
        return iter(self.objects.values())

    def _iter_call_meth(self, method, *args, **kwargs):
        """ Call meth on this objects __iter__ """
        for obj in self:
            if hasattr(obj, method):
                f = op.methodcaller(method, *args, **kwargs)
                f(obj)

    #XXX Event handlers
    def on_draw(self):
        self._iter_call_meth('on_draw_first')
        self._iter_call_meth('on_draw')
        self._iter_call_meth('on_draw_last')

    def on_update(self, dt):
        self._iter_call_meth('on_update', dt)

        # -- remove all destroyed objects from the scene
        self.objects = {k:v for k,v in self.objects.items()
            if (hasattr(v, 'destroyed') and not v.destroyed) or not hasattr(v, 'destroyed')}

    def on_resize(self, *args):
        self._iter_call_meth('on_resize', *args)

    def on_key_press(self, *args):
        self._iter_call_meth('on_key_press', *args)

    def on_key_release(self, *args):
        self._iter_call_meth('on_key_release', *args)

    def on_mouse_press(self, *args):
        self._iter_call_meth('on_mouse_press', *args)

    def on_mouse_release(self, *args):
        self._iter_call_meth('on_mouse_release', *args)

    def on_mouse_drag(self, *args):
        self._iter_call_meth('on_mouse_drag', *args)

    def on_mouse_motion(self, *args):
        self._iter_call_meth('on_mouse_motion', *args)

    def on_mouse_scroll(self, *args):
        self._iter_call_meth('on_mouse_scroll', *args)

    def on_text(self, *args):
        self._iter_call_meth('on_text', *args)

    def on_text_motion(self, *args):
        self._iter_call_meth('on_text_motion', *args)

    def on_text_motion_select(self, *args):
        self._iter_call_meth('on_text_motion_select', *args)
