import pyglet as pg

class TextElement(pg.text.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs):

    def update(self, batch group):
        self.batch = batch
        self.foreground_group = group