import operator as op

class Scene(object):
    """ Container object to manage other objects """

    def __init__(self, name):
        super(Scene, self).__init__()
        self.name = name
        self.objects = dict()

    def add(self, name, obj):
        if name in self.objects.keys():
            raise ValueError(f"Object with name '{name}' already exists!")
        self.objects[name] = obj

    def add_many(self, **kwargs):
        for key, val in kwargs.items():
            self.add(key, val)

    def __getattr__(self, name):
        return self.objects.get(name, None)

    def __iter__(self):
        return iter(self.objects.values())

    def _objects_iter_call(self, method, *args, **kwargs):
        """ Call meth for all objects """
        for obj in self:
            if hasattr(obj, method):
                f = op.methodcaller(method, *args, **kwargs)
                f(obj)

    #XXX Event handlers
    def on_draw(self):
        self._objects_iter_call('on_draw_first')
        self._objects_iter_call('on_draw')
        self._objects_iter_call('on_draw_last')

    def on_update(self, dt):
        self._objects_iter_call('on_update', dt)

        # Remove all destroyed objects
        self.objects = {k:v for k,v in self.objects.items()
            if hasattr(v, 'destroyed') and not v.destroyed}

    def on_resize(self, *args):
        self._objects_iter_call('on_resize', *args)

    def on_key_press(self, *args):
        self._objects_iter_call('on_key_press', *args)

    def on_key_release(self, *args):
        self._objects_iter_call('on_key_release', *args)

    def on_mouse_press(self, *args):
        self._objects_iter_call('on_mouse_press', *args)

    def on_mouse_release(self, *args):
        self._objects_iter_call('on_mouse_release', *args)

    def on_mouse_drag(self, *args):
        self._objects_iter_call('on_mouse_drag', *args)

    def on_mouse_motion(self, *args):
        self._objects_iter_call('on_mouse_motion', *args)

    def on_mouse_scroll(self, *args):
        self._objects_iter_call('on_mouse_scroll', *args)

    def on_text(self, *args):
        self._objects_iter_call('on_text', *args)

    def on_text_motion(self, *args):
        self._objects_iter_call('on_text_motion', *args)

    def on_text_motion_select(self, *args):
        self._objects_iter_call('on_text_motion_select', *args)
