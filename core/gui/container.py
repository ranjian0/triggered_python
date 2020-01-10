import operator

from core.gui.widget import Widget


class Container(Widget):
    """Object to manage multiple widgets"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = []

    def _add(self, item):
        self.children.append(item)
        item.parent = self
        item._dirty = True

    def __iadd__(self, item):
        if isinstance(item, (list, tuple)):
            for it in item:
                self._add(it)
        else:
            self._add(item)
        return self

    def _remove(self, item):
        self.children.remove(item)
        item.parent = None
        self._dirty = True

    def __isub__(self, item):
        if isinstance(item, (list, tuple)):
            for it in item:
                self._remove(it)
        else:
            self._remove(item)
        return self

    def __iter__(self):
        return iter(self.children)

    def _iter_call_meth(self, method, *args, **kwargs):
        """ Call meth on this object's __iter__ """
        for obj in self:
            if hasattr(obj, method):
                f = operator.methodcaller(method, *args, **kwargs)
                f(obj)

    def determine_size(self):
        if self.parent:  # Ensures that we don't do this for Frames
            w, h = 0, 0
            for c in self.children:
                c.determine_size()
                w += c.w
                h += c.h
            self._w, self._h = w, h

    def on_draw(self):
        super().on_draw()
        self._iter_call_meth("on_draw")

    def on_update(self, dt):
        super().on_update(dt)
        self._iter_call_meth("on_update", dt)

    def on_resize(self, *args):
        super().on_resize(*args)
        self._iter_call_meth("on_resize", *args)

    def on_key_press(self, *args):
        super().on_key_press(*args)
        self._iter_call_meth("on_key_press", *args)

    def on_key_release(self, *args):
        super().on_key_release(*args)
        self._iter_call_meth("on_key_release", *args)

    def on_mouse_press(self, *args):
        super().on_mouse_press(*args)
        self._iter_call_meth("on_mouse_press", *args)

    def on_mouse_release(self, *args):
        super().on_mouse_release(*args)
        self._iter_call_meth("on_mouse_release", *args)

    def on_mouse_drag(self, *args):
        super().on_mouse_drag(*args)
        self._iter_call_meth("on_mouse_drag", *args)

    def on_mouse_motion(self, *args):
        super().on_mouse_motion(*args)
        self._iter_call_meth("on_mouse_motion", *args)

    def on_mouse_scroll(self, *args):
        super().on_mouse_scroll(*args)
        self._iter_call_meth("on_mouse_scroll", *args)

    def on_text(self, *args):
        super().on_text(*args)
        self._iter_call_meth("on_text", *args)

    def on_text_motion(self, *args):
        super().on_text_motion(*args)
        self._iter_call_meth("on_text_motion", *args)

    def on_text_motion_select(self, *args):
        super().on_text_motion_select(*args)
        self._iter_call_meth("on_text_motion_select", *args)
