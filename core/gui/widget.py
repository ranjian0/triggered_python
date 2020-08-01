import pyglet as pg
from core.math import Rect
from core.event import EventHandler


class Widget(EventHandler):
    """Base class for all widgets"""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.parent = None

        # -- position attributes
        self._x = kwargs.get("x", 0)
        self._y = kwargs.get("y", 0)

        # -- size attributes
        self._w = kwargs.get("w", 1)
        self._h = kwargs.get("h", 1)

        # -- margin and padding attributes
        # Margin( spacing between consecutive widgets)
        # Padding( spacing between widget elements and widget extents)
        self._margins = kwargs.get("margins", (5, 5))
        self._margin_x = kwargs.get("margin_x", self._margins[0])
        self._margin_y = kwargs.get("margin_y", self._margins[1])

        self._padding = kwargs.get("padding", (10, 0))
        self._padding_x = kwargs.get("padding_x", 10)
        self._padding_y = kwargs.get("padding_y", 0)

        # -- layout attributes
        self._rect = Rect(0, 0, 1, 1)

        # -- draw attributes
        self._batch = kwargs.get("batch", pg.graphics.Batch())
        self._group = kwargs.get("group", pg.graphics.OrderedGroup(0))

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

    def _get_margin(self):
        return self._margin

    def _set_margin(self, val):
        self._margin = val
        self._margin_x, self._margin_y = val
        self._dirty = True

    margin = property(_get_margin, _set_margin)

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
        for elem in self.elements.values():
            elem._batch.draw()

    def on_update(self, dt):
        if self._dirty:
            # -- update size
            self.determine_size()

            # # -- update batches and groups
            for v in self.shapes.values():
                v.update_batch(self._batch, self._group)
            for v in self.elements.values():
                v.update_batch(pg.graphics.Batch(), pg.graphics.OrderedGroup(1))
            self._dirty = False
