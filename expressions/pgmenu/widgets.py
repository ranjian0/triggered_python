import pygame as pg


class Label:
    def __init__(self, pos, text, font=None, font_size=32, font_color=pg.Color("white")):
        self.position = pos
        self.text = text
        self.font_color = font_color

        self.font = pg.font.Font(font, font_size)
        self.text_render = self.font.render(self.text, True, font_color)

    def draw(self, screen):
        rect = self.text_render.get_rect(center=self.position)
        screen.blit(self.text_render, rect)

    def update(self):
        self.text_render = self.font.render(self.text, True, self.font_color)


class MultiLineLabel:
    def __init__(self, pos, text, font=None, font_size=32, font_color=pg.Color("white"),
                 halign="CENTER", valign="CENTER"):
        self.position = pos
        self.text = text

        self.font = pg.font.Font(font, font_size)
        self.font_size = font_size
        self.color = font_color
        self.h_alignment = halign.upper()
        self.v_alignment = valign.upper()

    def draw(self, screen):
        _size = screen.get_size()

        lines = self.text.splitlines()[1:]
        for idx, l in enumerate(lines):
            # Determine x alignment
            l_size = self.font.size(l)[0]
            if self.h_alignment == "LEFT":
                off_x = self.position[0]
            elif self.h_alignment == "RIGHT":
                off_x = ((_size[0] - l_size) + self.position[0])
            else:
                off_x = ((_size[0] - l_size) / 2 + self.position[0])

            # Determine y alignment
            v_size = len(lines) * self.font_size
            if self.v_alignment == "TOP":
                off_y = ((idx * self.font_size) + self.position[1])
            elif self.v_alignment == "BOTTOM":
                off_y = ((_size[1] - v_size) + (idx * self.font_size) + self.position[1])
            else:
                off_y = ((_size[1] - v_size) / 2 + (idx * self.font_size) + self.position[1])

            screen.blit(self.font.render(l, True, self.color), (off_x, off_y))


class Hoverable:
    def __init__(self, default, hovered):
        self.hovered = False
        self.default_state = default
        self.hover_state = hovered

    def get_state(self):
        if self.hovered:
            return self.hover_state
        else:
            return self.default_state

    def update_hover(self, rect):
        if rect.collidepoint(pg.mouse.get_pos()):
            self.hovered = True
        else:
            self.hovered = False


class Clickable:
    def __init__(self):
        self.clicked = False
        self.callable = None

    def on_click(self, func):
        self.callable = func

    def update_click(self, rect):
        if self.callable:
            if rect.collidepoint(pg.mouse.get_pos()):
                self.callable()


class Button(Hoverable, Clickable):
    def __init__(self, pos, size, text, text_color=pg.Color("white"),
                 default_color=pg.Color("red"), hover_color=pg.Color("maroon")):
        Hoverable.__init__(self, default_color, hover_color)
        Clickable.__init__(self)

        self.position = pos
        self.size = size
        self.text = text

        self.text_color = text_color
        self.text_size = self.size[1]
        self.font = pg.font.Font(None, self.text_size)

        self.make_button()

    def make_button(self):
        self.image = pg.Surface(self.size).convert_alpha()
        self.image.fill(self.get_state())
        self.image_rect = self.image.get_rect(center=self.position)

        self.text_render = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_render.get_rect(center=self.position)

    def on_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.update_click(self.image_rect)

    def update(self):
        # Check for hovering
        self.update_hover(self.image_rect)

        # Update button
        self.make_button()

    def draw(self, screen):
        screen.blit(self.image, self.image_rect)
        screen.blit(self.text_render, self.text_rect)


class ImageButton(Hoverable, Clickable):
    def __init__(self, pos, size, default_image, hover_image):
        Hoverable.__init__(self, default_image, hover_image)
        Clickable.__init__(self)

        self.position = pos
        self.size = size

        self.make_button()

    def make_button(self):
        self.image = pg.transform.scale(self.get_state(), self.size)
        self.image_rect = self.image.get_rect(center=self.position)

    def update(self):
        # Check for hovering
        self.update_hover(self.image_rect)

        # Check for click
        self.update_click(self.image_rect)

        # Update button
        self.make_button()

    def draw(self, screen):
        screen.blit(self.image, self.image_rect)
