from core.gui.widget import Widget
from core.gui.elements import LabelElement


class Label(Widget):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = LabelElement(text, **kwargs)
        self.elements["text"] = self.content

    def _get_text(self):
        return self.elements["text"].text

    def _set_text(self, val):
        self.elements["text"].text = val

    text = property(_get_text, _set_text)

    def determine_size(self):
        font = self.content.document.get_font()
        height = font.ascent - font.descent

        self._w = max(self.content.content_width, self._w)
        self._h = max(height, self._h)

    def on_update(self, dt):
        if self._dirty:
            self.content.x = self.x
            self.content.y = self.y
        super().on_update(dt)
