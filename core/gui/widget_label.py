from core.math import Rect
from .widget import Widget
from ._element import TextElement

class Label(Widget):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.elements['text'] = TextElement(text, **kwargs)

    def update_elements(self):
        if self._dirty:
            elem = self.elements['text']

            elem.x = self.x
            elem.y = self.y
            self.w = elem.content_width
            self.h = elem.content_height
            self._rect = Rect(self._x, self._y, self._w, self._h)

        super().update_elements()
