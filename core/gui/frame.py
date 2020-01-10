import pyglet.gl as gl
from core.utils import reset_matrix
from core.gui.container import Container


class Frame(Container):
    """Root gui container"""

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def on_resize(self, w, h):
        self.x = 0
        self.y = h
        self.w = w
        self.h = h

    def on_draw(self):
        with reset_matrix(self.w, self.h):
            gl.glPushAttrib(gl.GL_ENABLE_BIT)
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            super().on_draw()

            gl.glPopAttrib()
