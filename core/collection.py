
class Collection:
    """ Base class to manage a collection of objects """

    def __init__(self, object_type):
        self._class = object_type
        self._items = []

    def __iter__(self):
        for item in self._items:
            yield item

    def add(self, *args, **kwargs):
        """ Add a single object of type self._class to the collection """
        obj = self._class(*args, **kwargs)
        self._items.append(obj)

    def add_many(self, count, *args, **kwargs):
        """ Add count objects of type self._class to the collection """
        for idx in range(count):
            kw = {k:v[idx] for k,v in kwargs.items()}
            arg = () if not len(args) else args[idx]
            self.add(*arg, **kw)

    def on_draw(self):
        for item in self:
            if hasattr(item, 'on_draw'):
                item.on_draw()

    def on_update(self, dt):
        for item in self:
            if hasattr(item, 'on_update'):
                item.on_update(dt)

        # -- remove destroyed items from the collection
        destroyed = [self._items.index(item) for item in self if hasattr(item, 'destroyed') and item.destroyed]
        for idx in destroyed:
            del self._items[idx]