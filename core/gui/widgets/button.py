import pyglet as pg

from core.math import Rect

from core.gui.widget import Widget
from core.gui.shapes import RectangleShape
from core.gui.elements import LabelElement


class BaseButton(Widget):
    """ Base class for button behaviour """

    STATE_DEFAULT = 1
    STATE_PRESSED = 2
    STATE_HOVERED = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callback = kwargs.get("callback", None)
        self._hover_color = kwargs.get("hover_color", (200, 200, 0, 255))
        self._state = BaseButton.STATE_DEFAULT

    def on_mouse_motion(self, x, y, dx, dy):
        if self._rect.hit_test(x, y):
            self._state = BaseButton.STATE_HOVERED
        else:
            self._state = BaseButton.STATE_DEFAULT
        self._dirty = True

    def on_mouse_press(self, x, y, button, mod):
        if button == pg.window.mouse.LEFT:
            if self._rect.hit_test(x, y):
                self._state = BaseButton.STATE_PRESSED
                self._dirty = True

                if self._callback:
                    self._callback()

    def on_mouse_release(self, x, y, button, mod):
        if button == pg.window.mouse.LEFT:
            if self._state == BaseButton.STATE_PRESSED:
                self._state = BaseButton.STATE_DEFAULT
                self._dirty = True


class TextButton(BaseButton):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = LabelElement(
            text, **{k: v for k, v in kwargs.items() if k in dir(pg.text.Label)}
        )
        self.elements["text"] = self.content
        self.shapes["background"] = RectangleShape()

        self._radius = kwargs.get("radius", 0)
        self.shapes["background"].radius = self._radius

    def _get_text(self):
        return self.elements["text"].text

    def _set_text(self, val):
        self.elements["text"].text = val
        self._dirty = True

    text = property(_get_text, _set_text)

    def determine_size(self):
        font = self.content.document.get_font()
        height = font.ascent - font.descent

        self._w = max(self.content.content_width, self._w)
        self._h = max(height, self._h)

    def on_update(self, dt):
        if self._dirty:
            padx, pady = self._padding
            self.content.x = self.x + padx
            self.content.y = self.y - pady
            self._rect = Rect(self.x, self.y, self.w, self.h)

            background = self.shapes["background"]
            if self._state == BaseButton.STATE_DEFAULT:
                background.color = (100, 100, 100, 255)
            elif self._state == BaseButton.STATE_HOVERED:
                background.color = self._hover_color
            elif self._state == BaseButton.STATE_PRESSED:
                background.color = (200, 200, 200, 255)

            background.update(self.x, self.y, self.w, self.h)
        super().on_update(dt)
