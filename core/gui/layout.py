from core.gui.container import Container

VERTICAL = 1
HORIZONTAL = 2

ALIGN_TOP = 1
ALIGN_LEFT = 2
ALIGN_RIGHT = 3
ALIGN_CENTER = 4
ALIGN_BOTTOM = 5


class Layout(Container):
    """ Base class for arranging & sizing widgets """

    def __init__(self, axis, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._axis = axis
        self._align = kwargs.get("align", (ALIGN_CENTER, ALIGN_CENTER))

        # -- add children (alternative for quick definitions)
        if args:
            for item in args:
                self._add(item)

    def _layout(self):
        """ Arrange this containers children """
        alnx, alny = self._align
        padx, pady = self._padding
        magx, magy = self._margins

        # -- update the size and position of this container based on its parent, if any
        sx, sy = self.parent.size
        px, py = self.parent.position

        self._x, self._y = px + padx, py + pady
        for c in self.parent.children:
            if c == self:
                break
            if self._axis == VERTICAL:
                self._y -= c.h + magy
            elif self._axis == HORIZONTAL:
                self._x += c.w + magx

    def on_update(self, dt):
        if self._dirty:
            self._layout()
        super().on_update(dt)


class HLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(HORIZONTAL, *args, **kwargs)

    def _layout(self):
        super()._layout()

        width_accumulator = 0
        for c in self.children:
            c.x = self._x + width_accumulator
            c.y = self._y
            width_accumulator += c.w + self._margin_x


class VLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(VERTICAL, *args, **kwargs)

    def _layout(self):
        super()._layout()

        height_accumulator = 0
        for c in self.children:
            c.x = self._x
            c.y = self._y + height_accumulator
            height_accumulator -= c.h + self._margin_y
