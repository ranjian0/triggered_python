
class Drawable():
    def __init__(self, anchor="center", offset=(0,0)):
        super(Drawable, self).__init__()

        self.anchor = anchor
        self.offset = offset
        self.calc_pos(anchor, offset)

    def calc_pos(self, anchor, off):
        # -- calculate relative screen position based on anchor and offset
        display  = pg.display.get_surface()
        rect = display.get_rect().copy()

        self.pos = (0, 0)
        if anchor == 'center':
            px, py = rect.center
            px += off[0]
            py += off[1]
            self.pos = (px, py)

    def draw(self, surface):
        pass

    def update(self, dt):
        pass

    def event(self, event):
        pass

class Label(Drawable):
    """Text rendering widget"""
    def __init__(self, text, position,
                    font_size   = 25,
                    fg          = pg.Color("white"),
                    bg          = None):

        super(Label, self).__init__()
        pg.font.init()

        self.fg   = fg
        self.bg   = bg
        self.pos  = position
        self.text = text
        self.size = font_size

        self.font    = pg.font.Font(None, self.size)
        self.surface = self.font.render(self.text, True, self.fg, self.bg)
        self.rect    = self.surface.get_rect(center=self.pos)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

class Button(Drawable):
    """Button widget"""
    def __init__(self, text, size, position,
                    fg          = pg.Color("white"),
                    bg          = pg.Color("red"),
                    on_clicked  = lambda : print("Button Clicked"),
                    font_size   = 25,
                    hover_color = pg.Color("yellow")):

        super(Button, self).__init__()
        self.text = text
        self.size = size
        self.pos  = position

        self.foreground = fg
        self.background = bg
        self.on_clicked = on_clicked
        self.hover_col  = hover_color

        self.surface = pg.Surface(size)
        self.rect    = self.surface.get_rect(center=self.pos)
        self.label   = Label(self.text, (size[0]/2, size[1]/2), font_size, fg)

        self.state_hovered = False

    def draw(self, surface):

        if self.state_hovered:
            self.surface.fill(self.hover_col)
        else:
            self.surface.fill(self.background)

        self.label.draw(self.surface)
        surface.blit(self.surface, self.rect)

    def update(self, dt):
        mouse = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.state_hovered = True
        else:
            self.state_hovered = False

    def event(self, event):
        if self.state_hovered:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if callable(self.on_clicked):
                    self.on_clicked()

class Timer(Drawable):
    """Timer Widget"""
    def __init__(self, size, position,
                    start_value = 10,
                    fg          = pg.Color("green"),
                    bg          = pg.Color("black"),
                    on_complete = lambda : print("Timer Complete")):

        super(Timer, self).__init__()

        self.size  = size
        self.pos   = position
        self.start = start_value
        self.value = start_value

        self.foreground  = fg
        self.background  = bg
        self.on_complete = on_complete

        self.elapsed     = 0
        self.completed   = False

        self.surface = pg.Surface(self.size)
        self.rect    = self.surface.get_rect(center=self.pos)

    def reset(self):
        self.value = self.start

    def draw(self, surface):
        r = pg.Rect((0, 0), self.size)
        pg.draw.rect(self.surface, self.background, r)

        r = r.inflate(-10, -10)
        r.center = (self.size[0]/2, self.size[1]/2)
        r.width  *= self.value/self.start
        pg.draw.rect(self.surface, self.foreground, r)

        surface.blit(self.surface, self.rect)

    def update(self, dt):
        self.elapsed += dt

        if not self.completed and self.elapsed < self.start:
            self.value = self.start - self.elapsed
        elif not self.completed and self.elapsed >= self.start:
            self.value     = self.start
            if callable(self.on_complete):
                self.on_complete()
