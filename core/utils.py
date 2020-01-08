#  Copyright 2019 Ian Karanja <karanjaichungwa@gmail.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import ctypes
import pyglet.gl as gl
from contextlib import contextmanager


def set_flag(name, value, items):
    for item in items:
        setattr(item, name, value)


@contextmanager
def profile(perform=True):
    if perform:
        import io
        import pstats
        import cProfile

        s = io.StringIO()
        pr = cProfile.Profile()

        pr.enable()
        yield
        pr.disable()

        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats("cumtime")
        # ps.strip_dirs()
        ps.print_stats()

        all_stats = s.getvalue().split("\n")
        self_stats = "".join(
            [
                line + "\n"
                for idx, line in enumerate(all_stats)
                if ("triggered" in line) or (idx <= 4)
            ]
        )
        print(self_stats)
    else:
        yield


@contextmanager
def reset_matrix(w, h):
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, w, 0, h, -1, 1)

    yield

    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()


def draw_point(pos, color=(1, 0, 0, 1), size=5):
    gl.glColor4f(*color)
    gl.glPointSize(size)

    gl.glBegin(gl.GL_POINTS)
    gl.glVertex2f(*pos)
    gl.glEnd()
    # -- reset color
    gl.glColor4f(1, 1, 1, 1)


def draw_line(start, end, color=(1, 1, 0, 1), width=2):
    gl.glColor4f(*color)
    gl.glLineWidth(width)

    gl.glBegin(gl.GL_LINES)
    gl.glVertex2f(*start)
    gl.glVertex2f(*end)
    gl.glEnd()
    # -- reset color
    gl.glColor4f(1, 1, 1, 1)


def draw_path(points, color=(1, 0, 1, 1), width=5):
    gl.glColor4f(*color)
    gl.glLineWidth(width)

    gl.glBegin(gl.GL_LINE_STRIP)
    for point in points:
        gl.glVertex2f(*point)
    gl.glEnd()
    # -- reset color
    gl.glColor4f(1, 1, 1, 1)


def image_set_size(img, w, h):
    img.width = w
    img.height = h


def image_set_anchor_center(img):
    img.anchor_x = img.width / 2
    img.anchor_y = img.height / 2


def mouse_over_rect(mouse, center, size):
    mx, my = mouse
    tx, ty = center
    dx, dy = abs(tx - mx), abs(ty - my)

    tsx, tsy = size
    if dx < tsx / 2 and dy < tsy / 2:
        return True
    return False


def get_gl_translation():
    """ return global gl translation """
    arr = ctypes.c_double * 16
    mat = arr(*list(range(16)))
    gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX, mat)
    return list(mat)[-4:-1]


def global_position(x, y):
    """ convert x,y from relative to absolute global position """
    tx, ty, tz = get_gl_translation()
    # XXX : Negate because camera translates against center
    return -tx + x, -ty + y
