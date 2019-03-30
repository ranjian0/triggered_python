import pyglet as pg
import operator as op
from collections import namedtuple

Bounds = namedtuple('_Bounds',
    "left bottom right top")

class Camera:

    def __init__(self):
        self._size = (1,1)
        self._scale = (1,1)
        self._offset = (0, 0)
        self._bounds = Bounds(-10000, -10000, 10000, 10000)

    def _get_size(self):
        return self._size
    def _set_size(self, sc):
        self._size = sc
    size = property(_get_size, _set_size)

    def _get_scale(self):
        return self._scale
    def _set_scale(self, sc):
        self._scale = sc
    scale = property(_get_scale, _set_scale)

    def _get_offset(self):
        return self._offset
    def _set_offset(self, off):
        ox, oy = off
        w, h = self._size
        self._offset = (-ox + w/2, -oy + h/2)
        self._update()
    offset = property(_get_offset, _set_offset)

    def _get_bounds(self):
        return self._bounds
    def _set_bounds(self, bnds):
        self._bounds = bnds
    bounds = property(_get_bounds, _set_bounds)

    def _update(self):
        pg.gl.glMatrixMode(pg.gl.GL_MODELVIEW)
        pg.gl.glLoadIdentity()
        pg.gl.glTranslatef(*self._offset, 0)

