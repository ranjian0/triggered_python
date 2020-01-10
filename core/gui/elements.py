import pyglet as pg


class LabelElement(pg.text.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anchor_y = "top"
        self.anchor_x = "left"

    def update_batch(self, batch, group):
        self.batch = batch
        layout = pg.text.layout

        self.top_group = layout.TextLayoutGroup(group)
        self.background_group = pg.graphics.OrderedGroup(0, self.top_group)
        self.foreground_group = layout.TextLayoutForegroundGroup(
            1, self.top_group
        )
        self.foreground_decoration_group = layout.TextLayoutForegroundDecorationGroup(
            2, self.top_group
        )
        self._update()


class InputElement(object):
    def __init__(self, text):
        self.document = pg.text.document.UnformattedDocument(text)
        self.layout = pg.text.layout.IncrementalTextLayout(
            self.document, 1, 1, multiline=False
        )
        self.caret = pg.text.caret.Caret(self.layout)

    def _get_text(self):
        return self.document.text

    def _set_text(self, text):
        self.document.text = text

    text = property(_get_text, _set_text)

    def update_batch(self, batch, group):
        self.caret.delete()
        self.layout.delete()

        # workaround for pyglet issue 408
        self.layout.batch = None
        if self.layout._document:
            self.layout._document.remove_handlers(self.layout)
        self.layout._document = None
        # end workaround

        self.layout = pg.text.layout.IncrementalTextLayout(
            self.document,
            self.layout.width,
            self.layout.height,
            multiline=False,
            batch=batch,
            group=group,
        )
        self.caret = pg.text.caret.Caret(self.layout)
        self.caret.visible = False
