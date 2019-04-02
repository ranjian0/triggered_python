import pyglet as pg
import operator as op
from core.math import Vec2, Bounds, clamp

class Camera:

    def __init__(self):
        self._speed = 100
        self._size = Vec2(1,1)
        self._scale = Vec2(1,1)
        self._offset = Vec2(0, 0)
        self._bounds = Bounds(-1, -100, 10000, 10000)
        self._position = Vec2(0, 0)

    def _get_speed(self):
        return self._speed
    def _set_speed(self, sc):
        self._speed = Vec2(sc)
    speed = property(_get_speed, _set_speed)

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
        self._bounds = bnds if isinstance(bnds, Bounds) else Bounds(*bnds)
    bounds = property(_get_bounds, _set_bounds)

    def follow(self, position):
        sx, sy = self.size/2
        px, py = position
        position = Vec2(clamp(px, self.bounds.left+sx, self.bounds.right-sx),
            clamp(py, self.bounds.bottom+sy, self.bounds.top-sy))

        self.offset = self._size/2 - position

    def on_update(self, dt):
        """ Move the camera steadily against offset """
        epsilon = 1.0
        dist = self.offset.get_dist_sqrd(self._position)
        norm = (self.offset - self._position).normalized()
        if dist >= epsilon:
            #XXX NOTE: dist is added to speed to prevent camera from lagging behind
            self._position += norm * dt * (self.speed + dist)

        pg.gl.glMatrixMode(pg.gl.GL_MODELVIEW)
        pg.gl.glLoadIdentity()
        pg.gl.glTranslatef(*self._position, 0)
        pg.gl.glScalef(*self._scale, 1)

