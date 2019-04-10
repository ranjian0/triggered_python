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

import pyglet as pg
from resources import Resources
from pyglet.window import key, mouse

from .utils import *
from .event import EventType

class TextInput:

    def __init__(self, text, x, y, width, batch=None):
        self.batch = batch

        self.document = pg.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), dict(color=(0, 0, 0, 255)))
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pg.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=self.batch)
        self.caret = pg.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.add_background(x - pad, y - pad,
                            x + width + pad, y + height + pad)

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

    def add_background(self, x1, y1, x2, y2):
        vert_list = self.batch.add(4, pg.gl.GL_QUADS, None,
                                     ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', [200, 200, 220, 255] * 4))

class Button(object):

    def __init__(self):
        self._callback = None
        self._callback_args = ()

    def on_click(self, action, *args):
        if callable(action):
            self._callback = action
            self._callback_args = args

    def hover(self, x, y):
        return NotImplementedError()

    def on_mouse_motion(self, x, y, dx, dy):
        self.hover(x, y)

    def on_mouse_press(self, x, y, button, mod):
        if button == mouse.LEFT:
            if self.hover(x,y):
                self._callback(*self._callback_args)


class TextButton(pg.text.Label, Button):

    def __init__(self, *args, **kwargs):
        pg.text.Label.__init__(self, *args, **kwargs)
        Button.__init__(self)

        self._start_color = self.color
        self._hover_color = (200, 0, 0, 255)

    def _set_hcolor(self, val):
        self._hover_color = val
    hover_color = property(fset=_set_hcolor)

    def get_size(self):
        return self.content_width, self.content_height

    def hover(self, x, y):
        center = self.x, self.y
        if mouse_over_rect((x,y), center, self.get_size()):
            self.color = self._hover_color
            return True

        self.color = self._start_color
        return False

class ImageButton(Button):

    def __init__(self, image, position):
        Button.__init__(self)
        self.image = Resources.instance.sprite(image)
        image_set_anchor_center(self.image)

        self.x, self.y = position
        self.sprite = pg.sprite.Sprite(self.image, x=self.x, y=self.y)

    def update(self, px, py):
        self.x, self.y = px, py
        self.sprite.update(x=px, y=py)

    def hover(self, x, y):
        center = self.x, self.y
        size = self.sprite.width, self.sprite.height

        if mouse_over_rect((x,y), center, size):
            return True
        return False

    def draw(self):
        self.sprite.draw()
