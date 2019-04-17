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

class Widget(object):
    """Base class for all widgets"""
    def __init__(self, *args, **kwargs):
        super().__init__()
        # -- position attributes
        self._x = kwargs.get('x', 0)
        self._y = kwargs.get('y', 0)

        # -- size attributes
        self._w = kwargs.get('w', 1)
        self._h = kwargs.get('h', 1)

        # -- layout attributes
        self._rect = Rect(0, 0, 1, 1)

        # -- draw attributes
        self._batch = kwargs.get('batch', pg.graphics.Batch())
        self._group = kwargs.get('group', pg.graphics.OrderedGroup(0))

        self._dirty = False
        self.shapes = dict()
        self.elements = dict()

    def _get_x(self):
        return self._x
    def _set_x(self, val):
        self._x = val
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y
    def _set_y(self, val):
        self._y = val
    y = property(_get_y, _set_y)
    position = property(lambda self: (self._x, self._y))

    def _get_w(self):
        return self._w
    def _set_w(self, val):
        self._w = val
    w = property(_get_w, _set_w)

    def _get_h(self):
        return self._h
    def _set_h(self, val):
        self._h = val
    h = property(_get_h, _set_h)
    size = property(lambda self: (self._w, self._h))

    def _get_batch(self):
        return self._batch
    batch = property(_get_batch)

    def _get_group(self):
        return self._group
    group = property(_get_group)

    def on_draw(self):
        self._batch.draw()

    def on_update(self, dt):
        pass

    def on_resize(self, *args):
        pass

    def on_key_press(self, *args):
        pass

    def on_key_release(self, *args):
        pass

    def on_mouse_press(self, *args):
        pass

    def on_mouse_release(self, *args):
        pass

    def on_mouse_drag(self, *args):
        pass

    def on_mouse_motion(self, *args):
        pass

    def on_mouse_scroll(self, *args):
        pass

    def on_text(self, *args):
        pass

    def on_text_motion(self, *args):
        pass

    def on_text_motion_select(self, *args):
        pass

class Container(Widget):
    """Object to manage multiple widgets"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = []

    def _add(self, item):
        self.children.append(item)

    def __iadd__(self, item):
        if isinstance(item, (list, tuple)):
            for it in item:
                self._add(it)
        else:
            self._add(item)
        return self

    def _remove(self, item):
        self.children.remove(item)

    def __isub__(self, item):
        if isinstance(item, (list, tuple)):
            for it in item:
                self._remove(it)
        else:
            self._remove(item)
        return self

    def __iter__(self):
        return iter(self.children)

    def _iter_call_meth(self, method, *args, **kwargs):
        """ Call meth on this object's __iter__ """
        for obj in self:
            if hasattr(obj, method):
                f = operator.methodcaller(method, *args, **kwargs)
                f(obj)

    def on_draw(self):
        super().on_draw()
        self._iter_call_meth('on_draw')

    def on_update(self, dt):
        super().on_update(dt)
        self._iter_call_meth('on_update', dt)

    def on_resize(self, *args):
        super().on_resize(*args)
        self._iter_call_meth('on_resize', *args)

    def on_key_press(self, *args):
        super().on_key_press(*args)
        self._iter_call_meth('on_key_press', *args)

    def on_key_release(self, *args):
        super().on_key_release(*args)
        self._iter_call_meth('on_key_release', *args)

    def on_mouse_press(self, *args):
        super().on_mouse_press(*args)
        self._iter_call_meth('on_mouse_press', *args)

    def on_mouse_release(self, *args):
        super().on_mouse_release(*args)
        self._iter_call_meth('on_mouse_release', *args)

    def on_mouse_drag(self, *args):
        super().on_mouse_drag(*args)
        self._iter_call_meth('on_mouse_drag', *args)

    def on_mouse_motion(self, *args):
        super().on_mouse_motion(*args)
        self._iter_call_meth('on_mouse_motion', *args)

    def on_mouse_scroll(self, *args):
        super().on_mouse_scroll(*args)
        self._iter_call_meth('on_mouse_scroll', *args)

    def on_text(self, *args):
        super().on_text(*args)
        self._iter_call_meth('on_text', *args)

    def on_text_motion(self, *args):
        super().on_text_motion(*args)
        self._iter_call_meth('on_text_motion', *args)

    def on_text_motion_select(self, *args):
        super().on_text_motion_select(*args)
        self._iter_call_meth('on_text_motion_select', *args)
