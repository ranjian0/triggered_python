import pyglet as pg
from pyglet.gl import *
from .container import Container

class Frame(Container):
    """Root gui container"""
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def update_batch(self, batch, group):
        self._batch, self._group = batch, group
        count = len(self._children)
        for c, i in zip(self._children, range(count-1, -1, -1)):
            order = pg.graphics.OrderedGroup(i, group)
            c.update_batch(batch, order)

    def _add(self, child):
        super()._add(child)
        self.update_batch(pg.graphics.Batch(), self._group)

    def _remove(self, child):
        super()._remove(child)
        self.update_batch(pg.graphics.Batch(), self._group)

    def on_draw(self):
        self.update_global_coords()
        self.update_elements()

        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.batch.draw()

        glPopAttrib()
