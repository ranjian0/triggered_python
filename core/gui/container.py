from .widget import Widget

class Container(Widget):
    """Object to manage multiple widgets"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._children = []

    def _add(self, item):
        self._children.append(item)
        item.parent = self

        item.update_batch(self._batch, self._group)
        self.root.update_layout()

    def __iadd__(self, item):
        self._add(item)
        return self

    def _remove(self, item):
        self._children.remove(item)
        item.parent = None

        item.update_batch(None, None)
        self.root.update_layout()

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

    def update_batch(self, batch, group):
        super().update_batch(batch, group)
        self._iter_call_meth("update_batch", batch, group)

    def on_update(self, dt):
        super().on_update(dt)
        self._iter_call_meth('on_update', dt)

    def on_resize(self, *args):
        super().on_resize(*args)
        self._iter_call_meth('on_resize', *args)

    def on_key_press(self, *args):
        super().on_key_press(*args)
        self._iter_call_meth('on_key_press', *args)

    def on_key_release(self, *args):
        super().on_key_release(*args)
        self._iter_call_meth('on_key_release', *args)

    def on_mouse_press(self, *args):
        super().on_mouse_press(*args)
        self._iter_call_meth('on_mouse_press', *args)

    def on_mouse_release(self, *args):
        super().on_mouse_release(*args)
        self._iter_call_meth('on_mouse_release', *args)

    def on_mouse_drag(self, *args):
        super().on_mouse_drag(*args)
        self._iter_call_meth('on_mouse_drag', *args)

    def on_mouse_motion(self, *args):
        super().on_mouse_motion(*args)
        self._iter_call_meth('on_mouse_motion', *args)

    def on_mouse_scroll(self, *args):
        super().on_mouse_scroll(*args)
        self._iter_call_meth('on_mouse_scroll', *args)

    def on_text(self, *args):
        super().on_text(*args)
        self._iter_call_meth('on_text', *args)

    def on_text_motion(self, *args):
        super().on_text_motion(*args)
        self._iter_call_meth('on_text_motion', *args)

    def on_text_motion_select(self, *args):
        super().on_text_motion_select(*args)
        self._iter_call_meth('on_text_motion_select', *args)
