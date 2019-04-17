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
from math import pi, sin, cos

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
        self._dirty = True

    def __iadd__(self, item):
        if isinstance(item, (list, tuple)):
            for it in item:
                self._add(it)
        else:
            self._add(item)
        return self

    def _remove(self, item):
        self.children.remove(item)
        self._dirty = True

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

class Layout(Container):
    """ Base class for arranging & sizing widgets """
    VERTICAL = 1
    HORIZONTAL = 2

    ALIGN_TOP    = 1
    ALIGN_LEFT   = 2
    ALIGN_RIGHT  = 3
    ALIGN_CENTER = 4
    ALIGN_BOTTOM = 5
    def __init__(self, axis, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._axis = axis
        self._align = kwargs.get("align", (ALIGN_LEFT, ALIGN_TOP))
        self._padding = kwargs.get("padding", (5, 5))

        # -- add children (alternative for quick definitions)
        if args:
            for item in args:
                self._add(item)

class HLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(Layout.HORIZONTAL, *args, **kwargs)

class VLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(Layout.VERTICAL, *args, **kwargs)

class Frame(Container):
    """Root gui container"""
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def on_draw(self):
        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        super().draw()

        glPopAttrib()


class RectangleShape:

    def __init__(self, x, y, w, h,
                    color=(100, 100, 100, 255), radius=0):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._color = color
        self._radius = radius

        self._batch = pg.graphics.Batch()
        self._group = pg.graphics.OrderedGroup(0)
        self._vertices = None
        self._update()

    def _get_x(self):
        return self._x
    def _set_x(self, val):
        self._x = val
        self._update()
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y
    def _set_y(self, val):
        self._y = val
        self._update()
    y = property(_get_y, _set_y)

    def _get_w(self):
        return self._w
    def _set_w(self, val):
        self._w = val
        self._update()
    w = property(_get_w, _set_w)

    def _get_h(self):
        return self._h
    def _set_h(self, val):
        self._h = val
        self._update()
    h = property(_get_h, _set_h)

    def _get_color(self):
        return self._color
    def _set_color(self, val):
        self._color = val
        self._update()
    color = property(_get_color, _set_color)

    def _get_radius(self):
        return self._radius
    def _set_radius(self, val):
        self._radius = val
        self._update()
    radius = property(_get_radius, _set_radius)

    def update_batch(self, batch, group):
        self._batch, self._group = batch, group
        if self._vertices:
            self._vertices.delete()
            self._vertices = None

        self._update()

    def _update(self):
        x, y, w, h = self._x, self._y, self._w, self._h

        if radius == 0:
            x1, y1 = x, y
            x2, y2 = x + w, y - h
            self._vertices = self._batch.add(4, pg.gl.GL_POLYGON, self._group,
                                     ('v2f', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', self._color * 4))


        else:
            # -- create circle vertices
            resolution = 32
            arc = (2*pi) / resolution
            x += self._radius
            y -= self._radius
            w -= self._radius*2
            h -= self._radius*2

            transform = [
                (x+w, y),   # - top right
                (x,   y),   # - top left
                (x,   y-h), # - bottom left
                (x+w, y-h), # - bottom right
            ]

            tindex = 0
            circle = []
            for r in range(resolution):
                angle = r*arc
                if r > resolution//4:
                    tindex = 1
                if r > resolution//2:
                    tindex = 2
                if r > resolution*.75:
                    tindex = 3
                tx, ty = transform[tindex]
                circle.extend([tx + cos(angle)*self._radius, ty + sin(angle)*self._radius])

            self._vertices = self._batch.add(len(circle)//2, pg.gl.GL_POLYGON, self._group,
                                 ('v2f', circle),
                                 ('c4B', self._color * (len(circle)//2)))

class CircleShape:

    def __init__(self, x, y, radius, color=(100, 100, 100, 255)):
        self._x = x
        self._y = y
        self._color = color
        self._radius = radius

        self._batch = pg.graphics.Batch()
        self._group = pg.graphics.OrderedGroup(0)
        self._vertices = None
        self._update()


    def _get_x(self):
        return self._x
    def _set_x(self, val):
        self._x = val
        self._update()
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y
    def _set_y(self, val):
        self._y = val
        self._update()
    y = property(_get_y, _set_y)

    def _get_color(self):
        return self._color
    def _set_color(self, val):
        self._color = val
        self._update()
    color = property(_get_color, _set_color)

    def _get_radius(self):
        return self._radius
    def _set_radius(self, val):
        self._radius = val
        self._update()
    radius = property(_get_radius, _set_radius)

    def update_batch(self, batch, group):
        self._batch, self._group = batch, group
        if self._vertices:
            self._vertices.delete()
            self._vertices = None

        self._update()

    def _update(self):
        resolution = 64
        arc = (2*pi) / resolution

        circle = []
        for r in range(resolution):
            angle = r*arc
            circle.extend([self._x + cos(angle)*self._radius, self._y + sin(angle)*self._radius])

        self._vertices = self._batch.add(len(circle)//2, pg.gl.GL_POLYGON, self._group,
                             ('v2f', circle),
                             ('c4B', self._color * (len(circle)//2)))


class LabelElement(pg.text.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anchor_y = "top"
        self.anchor_x = "left"

    def update_batch(self, batch, group):
        self.batch = batch

        self.top_group = pg.text.layout.TextLayoutGroup(group)
        self.background_group = pg.graphics.OrderedGroup(0, self.top_group)
        self.foreground_group = pg.text.layout.TextLayoutForegroundGroup(1, self.top_group)
        self.foreground_decoration_group = pg.text.layout.TextLayoutForegroundDecorationGroup(2, self.top_group)
        self._update()

class InputElement(object):
    def __init__(self, text):
        self.document = pg.text.document.UnformattedDocument(text)
        self.layout = pg.text.layout.IncrementalTextLayout(self.document, 1, 1, multiline=False)
        self.caret = pg.text.caret.Caret(self.layout)

    def _get_text(self):
        return self.document.text
    def _set_text(self, text):
        self.document.text = text
    text = property(_get_text, _set_text)

    def update_batch(self, batch, group):
        self.caret.delete()
        self.layout.delete()

        ### workaround for pyglet issue 408
        self.layout.batch = None
        if self.layout._document:
            self.layout._document.remove_handlers(self.layout)
        self.layout._document = None
        ### end workaround

        self.layout = pg.text.layout.IncrementalTextLayout(self.document,
            self.layout.width, self.layout.height, multiline=False, batch=batch, group=group)
        self.caret = pg.text.caret.Caret(self.layout)
        self.caret.visible = False
