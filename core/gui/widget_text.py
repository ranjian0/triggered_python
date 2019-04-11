from .widget import Widget
from .gui_element import TextElement

class Text(Widget):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.elements['text'] = TextElement(text, **kwargs)

    def update_layout(self):
        if self._dirty:
            elem = self.elements['text']

            elem.x = self.x
            elem.y = self.y
            self.w = elem.content_width
            self.h = elem.content_height

        super().update_layout()
