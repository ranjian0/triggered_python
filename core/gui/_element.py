import pyglet as pg

class LabelElement(pg.text.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anchor_y = "top"
        self.anchor_x = "left"

    def update_batch(self, batch, group):
        self.batch = batch

        self.top_group = pg.text.layout.TextLayoutGroup(group)
        self.background_group = pg.graphics.OrderedGroup(0, self.top_group)
        self.foreground_group = pg.text.layout.TextLayoutForegroundGroup(1, self.top_group)
        self.foreground_decoration_group = pg.text.layout.TextLayoutForegroundDecorationGroup(2, self.top_group)
        self._update()