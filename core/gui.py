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

import math
import operator
import pyglet as pg
from pyglet.gl import *
from .math import Rect

class Widget(object):
    """Base class for all widgets"""
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.parent = None

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
        self._dirty = True
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y
    def _set_y(self, val):
        self._y = val
        self._dirty = True
    y = property(_get_y, _set_y)
    position = property(lambda self: (self._x, self._y))

    def _get_w(self):
        return self._w
    def _set_w(self, val):
        self._w = val
        self._dirty = True
    w = property(_get_w, _set_w)

    def _get_h(self):
        return self._h
    def _set_h(self, val):
        self._h = val
        self._dirty = True
    h = property(_get_h, _set_h)
    size = property(lambda self: (self._w, self._h))

    def _get_batch(self):
        return self._batch
    batch = property(_get_batch)

    def _get_group(self):
        return self._group
    group = property(_get_group)

    def determine_size(self):
        pass

    def on_draw(self):
        self._batch.draw()

    def on_update(self, dt):
        if self._dirty:
            # -- update size
            self.determine_size()

            # -- update batches and groups
            for k.v in self.shapes.items():
                v.update_batch(self._batch, self._group)
            for k,v in self.elements.items():
                v.update_batch(self._batch, self._group)
            self._dirty = False

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
        item.parent = self
        item._dirty = True
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
        item.parent = None
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

    def determine_size(self):
        if self.parent: # Ensures that we don't do this for Frames
            w, h = 0, 0
            for c in self.children:
                c.determine_size()
                w += c.w
                h += c.h
            self._w, self._h = w, h

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
        self._align = kwargs.get("align", (Layout.ALIGN_LEFT, Layout.ALIGN_TOP))
        self._padding = kwargs.get("padding", (5, 5))
        self._margins = kwargs.get("margin", (15, 15))

        # -- add children (alternative for quick definitions)
        if args:
            for item in args:
                self._add(item)

    def _get_align(self):
        align_map = {
            "top"       : Layout.ALIGN_TOP,
            "left"      : Layout.ALIGN_LEFT,
            "right"     : Layout.ALIGN_RIGHT,
            "center"    : Layout.ALIGN_CENTER,
            "bottom"    : Layout.ALIGN_BOTTOM
        }

        ax, ay = self._align
        if isinstance(ax, str):
            ax = align_map.get(ax.lower(), None)
            if not ax:
                raise ValueError(f"Alignment must be str in {align_map.keys()}")
        if isinstance(ay, str):
            ay = align_map.get(ay.lower(), None)
            if not ay:
                raise ValueError(f"Alignment must be str in {align_map.keys()}")

        return ax, ay

    def _layout(self):
        """ Arrange this containers children """
        axis = self._axis
        padx, pady = self._padding
        marginx, marginy = self._margins
        alignx, aligny = self._get_align()

        # -- update the size and position of this container based on its parent, if any
        psx, psy = self.parent.size
        px, py = self.parent.position
        self._x, self._y = px + marginx, py - marginy
        for c in self.parent.children:
            if c == self: break
            if axis == Layout.VERTICAL:
                self._y -= c.h + pady
            elif axis == Layout.HORIZONTAL:
                self._X += c.w + padx


        # -- update position of children in this container
        if axis == Layout.HORIZONTAL:
            width_accumulator = 0
            for c in self.children:
                c.x = self._x + width_accumulator
                c.y = self._y
                width_accumulator += c.w + padx
            self._w = width_accumulator
            self._h = psy

        elif axis == Layout.VERTICAL:
            height_accumulator = 0
            for c in self.children:
                c.x = self._x
                c.y = self._y + height_accumulator
                height_accumulator -= c.h + pady
            self._w = psx
            self._h = height_accumulator

    def on_update(self, dt):
        if self._dirty:
            self._layout()
        super().on_update(dt)

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

    def on_resize(self, w, h):
        self.x = 0
        self.y = h
        self.w = w
        self.h = h

    def on_draw(self):
        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        super().on_draw()

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
            self._vertices = self._batch.add(4, GL_POLYGON, self._group,
                                     ('v2f', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', self._color * 4))


        else:
            # -- create circle vertices
            resolution = 32
            arc = (2*math.pi) / resolution
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
                circle.extend([tx + math.cos(angle)*self._radius, ty + math.sin(angle)*self._radius])

            self._vertices = self._batch.add(len(circle)//2, GL_POLYGON, self._group,
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
        arc = (2*math.pi) / resolution

        circle = []
        for r in range(resolution):
            angle = r*arc
            circle.extend([self._x + math.cos(angle)*self._radius, self._y + math.sin(angle)*self._radius])

        self._vertices = self._batch.add(len(circle)//2, GL_POLYGON, self._group,
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


class Label(Widget):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = LabelElement(text, **kwargs)
        self.elements['text'] = self.content

    def _get_text(self):
        return self.elements['text'].text
    def _set_text(self, val):
        self.elements['text'].text = val
    text = property(_get_text, _set_text)

    def determine_size(self):
        font = self.content.document.get_font()
        height = font.ascent - font.descent

        self._w = self.content.content_width
        self._h = height

    def on_update(self, dt):
        if self._dirty:
            self.content.x = self.x
            self.content.y = self.y
        super().on_update(dt)
