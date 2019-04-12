import operator
from .widget import Widget
from core.math import Rect


class Layout(Widget):
    """ Base class container for other widgets """

    VERTICAL = 1
    HORIZONTAL = 2
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = []

    def _add(self, item):
        item.parent = self
        self._children.append(item)
        self._dirty = True

    def __iadd__(self, item):
        self._add(item)
        return self

    def _remove(self, item):
        item.parent = None
        self._children.remove(item)
        self._dirty = True

    def __isub__(self, item):
        self._remove(item)
        return self

    def __iter__(self):
        return iter(self._children)

    def _iter_call_meth(self, method, *args, **kwargs):
        """ Call meth on this object's __iter__ """
        for obj in self:
            if hasattr(obj, method):
                f = operator.methodcaller(method, *args, **kwargs)
                f(obj)

    def on_draw(self):
        self.update_layout()
        self.batch.draw()

    def on_update(self, dt):
        self._iter_call_meth('on_update', dt)

    def on_resize(self, *args):
        self._iter_call_meth('on_resize', *args)

    def on_key_press(self, *args):
        self._iter_call_meth('on_key_press', *args)

    def on_key_release(self, *args):
        self._iter_call_meth('on_key_release', *args)

    def on_mouse_press(self, *args):
        self._iter_call_meth('on_mouse_press', *args)

    def on_mouse_release(self, *args):
        self._iter_call_meth('on_mouse_release', *args)

    def on_mouse_drag(self, *args):
        self._iter_call_meth('on_mouse_drag', *args)

    def on_mouse_motion(self, *args):
        self._iter_call_meth('on_mouse_motion', *args)

    def on_mouse_scroll(self, *args):
        self._iter_call_meth('on_mouse_scroll', *args)

    def on_text(self, *args):
        self._iter_call_meth('on_text', *args)

    def on_text_motion(self, *args):
        self._iter_call_meth('on_text_motion', *args)

    def on_text_motion_select(self, *args):
        self._iter_call_meth('on_text_motion_select', *args)


class BoxLayout(Layout):

    def __init__(self, orient, spacing=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orient = orient
        self._spacing = spacing

    def update_layout(self):
        for c in self._children:
            c.update_layout()

        if self._dirty:
            self._gx, self._gy = self.root.position

            w, h = 0, 0
            if self._orient == Layout.HORIZONTAL:
                h = max(c.h for c in self._children)
                w = sum(c.w + self._spacing for c in self._children)

                accumulator = 0
                for c in self._children:
                    c.y = self._gy
                    c.x = self._gx + accumulator
                    c.update_layout()
                    accumulator += c.w  + self._spacing

            elif self._orient == Layout.VERTICAL:
                w = max(c.w for c in self._children)
                h = sum(c.h + self._spacing for c in self._children)

                accumulator = 0
                for c in self._children:
                    c.x = self._gx
                    c.y = self._gy - accumulator
                    c.update_layout()
                    accumulator += c.h + self._spacing

            self._w, self._h = w, h
            self._rect = Rect(self._gx, self._gy, self._w, self._h)
            self.update_batch(self._batch, self._group)
        super().update_layout()

    def update_batch(self, batch, group):
        for c in self._children:
            c.update_batch(self._batch, self._group)


class HBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(Layout.HORIZONTAL, **kwargs)

class VBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(Layout.VERTICAL, **kwargs)
