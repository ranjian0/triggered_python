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
    def __init__(self, axis, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._axis = axis
        self._padding = kwargs.get("padding", 5)

        # -- add children
        if args:
            for item in args:
                self._add(item)



class HBoxLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(Layout.HORIZONTAL, *args, **kwargs)

class VBoxLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(Layout.VERTICAL, *args, **kwargs)
