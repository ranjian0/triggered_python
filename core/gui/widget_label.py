from core.math import Rect, Size
from .widget import Widget
from ._element import LabelElement

class Label(Widget):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.content = LabelElement(text, **kwargs)
        self.elements['text'] = self.content

    def update_elements(self):
        if self._dirty:
            self.content.x = self._gx
            self.content.y = self._gy

        super().update_elements()