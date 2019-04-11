import pyglet as pg
from math import pi, sin, cos

class RectangleShape:

    def __init__(self, x, y, w, h,
                    color=(100, 100, 100, 255), radius=0):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._color = color
        self._radius = radius

        self._batch = pg.graphics.Batch()
        self._group = pg.graphics.OrderedGroup(0)
        self._vertices = None
        self._update()

    def _get_x(self):
        return self._x
    def _set_x(self, val):
        self._x = val
        self._update()
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y
    def _set_y(self, val):
        self._y = val
        self._update()
    y = property(_get_y, _set_y)

    def _get_w(self):
        return self._w
    def _set_w(self, val):
        self._w = val
        self._update()
    w = property(_get_w, _set_w)

    def _get_h(self):
        return self._h
    def _set_h(self, val):
        self._h = val
        self._update()
    h = property(_get_h, _set_h)

    def _get_color(self):
        return self._color
    def _set_color(self, val):
        self._color = val
        self._update()
    color = property(_get_color, _set_color)

    def _get_radius(self):
        return self._radius
    def _set_radius(self, val):
        self._radius = val
        self._update()
    radius = property(_get_radius, _set_radius)

    def update(self, batch, group):
        self._batch = batch
        self._group = group
        self._update()

    def _update(self):
        x, y, w, h = self._x, self._y, self._w, self._h
        if self._vertices:
            self._vertices.delete()

        if radius == 0:
            x1, y1 = x, y
            x2, y2 = x + w, y - h
            self._vertices = self._batch.add(4, pg.gl.GL_POLYGON, self._group,
                                     ('v2f', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', self._color * 4))


        else:
            # -- create circle vertices
            resolution = 32
            arc = (2*pi) / resolution
            x += self._radius
            y -= self._radius
            w -= self._radius*2
            h -= self._radius*2

            transform = [
                (x+w, y),   # - top right
                (x,   y),   # - top left
                (x,   y-h), # - bottom left
                (x+w, y-h), # - bottom right
            ]

            tindex = 0
            circle = []
            for r in range(resolution):
                angle = r*arc
                if r > resolution//4:
                    tindex = 1
                if r > resolution//2:
                    tindex = 2
                if r > resolution*.75:
                    tindex = 3
                tx, ty = transform[tindex]
                circle.extend([tx + cos(angle)*self._radius, ty + sin(angle)*self._radius])

            self._vertices = self._batch.add(len(circle)//2, pg.gl.GL_POLYGON, self._group,
                                 ('v2f', circle),
                                 ('c4B', self._color * (len(circle)//2)))


class CircleShape:

    def __init__(self, x, y, radius, color=(100, 100, 100, 255)):
        self._x = x
        self._y = y
        self._color = color
        self._radius = radius

        self._batch = pg.graphics.Batch()
        self._group = pg.graphics.OrderedGroup(0)
        self._vertices = None
        self._update()


    def _get_x(self):
        return self._x
    def _set_x(self, val):
        self._x = val
        self._update()
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y
    def _set_y(self, val):
        self._y = val
        self._update()
    y = property(_get_y, _set_y)

    def _get_color(self):
        return self._color
    def _set_color(self, val):
        self._color = val
        self._update()
    color = property(_get_color, _set_color)

    def _get_radius(self):
        return self._radius
    def _set_radius(self, val):
        self._radius = val
        self._update()
    radius = property(_get_radius, _set_radius)

    def update(self, batch, group):
        self._batch = batch
        self._group = group
        self._update()

    def _update(self):
        if self._vertices:
            self._vertices.delete()

        resolution = 64
        arc = (2*pi) / resolution

        circle = []
        for r in range(resolution):
            angle = r*arc
            circle.extend([self._x + cos(r*arc)*self._radius, self._y + sin(r*arc)*self._radius])

        self._vertices = self._batch.add(len(circle)//2, pg.gl.GL_POLYGON, self._group,
                             ('v2f', circle),
                             ('c4B', self._color * (len(circle)//2)))
