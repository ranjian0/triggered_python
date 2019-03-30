import pyglet as pg
import operator as op
from core.math import Vec2, Bounds, clamp

class Camera:

    def __init__(self):
        self._damping = .25
        self._size = Vec2(1,1)
        self._scale = Vec2(1,1)
        self._offset = Vec2(0, 0)
        self._bounds = Bounds(-10000, -10000, 10000, 10000)

    def _get_damping(self):
        return self._damping
    def _set_damping(self, sc):
        self._damping = Vec2(sc)
    damping = property(_get_damping, _set_damping)

    def _get_size(self):
        return self._size
    def _set_size(self, sc):
        self._size = Vec2(sc)
    size = property(_get_size, _set_size)

    def _get_scale(self):
        return self._scale
    def _set_scale(self, sc):
        self._scale = Vec2(sc)
    scale = property(_get_scale, _set_scale)

    def _get_offset(self):
        return self._offset
    def _set_offset(self, off):
        self._offset = off if isinstance(off, Vec2) else Vec2(off)
    offset = property(_get_offset, _set_offset)

    def _get_bounds(self):
        return self._bounds
    def _set_bounds(self, bnds):
        self._bounds = bnds
    bounds = property(_get_bounds, _set_bounds)

    def follow(self, position):
        """ Calculate camera offset to position whilst staying within bounds """
        # -- calculate offset from center
        cam_pos = (self.size/2)
        offset  = position - cam_pos

        # -- clamp within bounds
        offset = Vec2(clamp(offset.x, self.bounds.left, self.bounds.right),
            clamp(offset.y, self.bounds.bottom, self.bounds.top))
        self.offset = -offset

    def on_update(self, dt):
        """ Move the camera steadily against offset """
        trans = self.offset * self.damping
        pg.gl.glMatrixMode(pg.gl.GL_MODELVIEW)
        pg.gl.glLoadIdentity()
        pg.gl.glTranslatef(*trans, 0)



