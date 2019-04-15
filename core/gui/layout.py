import operator
from core.math import Rect, Size
from .container import Container


class Layout(Container):
    """ Base class container arranging & sizing widgets """

    VERTICAL = 1
    HORIZONTAL = 2

    ALIGN_TOP    = 1
    ALIGN_LEFT   = 2
    ALIGN_RIGHT  = 3
    ALIGN_CENTER = 4
    ALIGN_BOTTOM = 5
    def __init__(self, axis, spacing=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._axis = axis
        self._spacing = spacing

        #XXX Extra box layout properties
        # -- make children fill layout
        self._expand = False
        # -- anchor children to layout position
        self._halign = Layout.ALIGN_LEFT
        self._valign = Layout.ALIGN_TOP

        # -- add children
        if args:
            for item in args:
                self._add(item)

    def expand(self, val):
        self._expand = val

    def align(self, horizontal=None, vertical=None):
        if horizontal not in ["left", "center", "right"]:
            raise ValueError('Expected str argument in {"left", "center", "right"}')
        if vertical not in ["top", "center", "bottom"]:
            raise ValueError('Expected str argument in {"top", "center", "bottom"}')

        if horizontal:
            self._halign = {"left":   Layout.ALIGN_LEFT,
                            "right":  Layout.ALIGN_RIGHT,
                            "center": Layout.ALIGN_CENTER}[horizontal]
        if vertical:
            self._valign = {"top":    Layout.ALIGN_TOP,
                            "center": Layout.ALIGN_CENTER,
                            "bottom": Layout.ALIGN_BOTTOM}[vertical]

    def determine_size(self):
        pass

    def reset_size(self, size):
        super().reset_size(size)
        pass


class HBoxLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(Layout.HORIZONTAL, *args, **kwargs)

class VBoxLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(Layout.VERTICAL, *args, **kwargs)
