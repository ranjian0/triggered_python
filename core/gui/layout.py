from .widget import Widget


class Layout(Widget):
    """ Base class container for other widgets """

    VERTICAL = 1
    HORIZONTAL = 2
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = []

    def _add(self, item):
        self._children.append(item)

    def __iadd__(self, item):
        self._add(item)

    def _remove(self, item):
        self._children.remove(item)

    def __isub__(self, item):
        self._children.remove(item)


class BoxLayout(Layout):

    def __init__(self, orient, spacing=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orient = orient
        self._spacing = spacing

    def update_layout(self):
        self._gx, self._gy = self._find_root().position

        w, h = 0, 0
        if self._orient == Layout.HORIZONTAL:
            h = max(c.h for c in self._children)
            w = sum(c.w + self._spacing for c in self._children)

            accumulator = 0
            for c in self._children:
                c.y = self._gy
                c.x = self._gx + accumulator
                accumulator += c.w  + self._spacing

        elif self._orient == 1:
            w = max(c.w for c in self._children)
            h = sum(c.h + self._spacing for c in self._children)

            accumulator = 0
            for c in self._children:
                c.x = self._gx
                c.y = self._gy + accumulator
                accumulator += c.h + self._spacing

        self._w, self._h = w, h
        self._rect = Rect(self._gx, self._gy, self._w, self._h)
        super().update_layout()

    def update_batch(self):
        for c in self._children:
            c.update_batch(self._batch, self._group)


class HBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(Layout.HORIZONTAL, **kwargs)

class VBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(Layout.VERTICAL, **kwargs)
