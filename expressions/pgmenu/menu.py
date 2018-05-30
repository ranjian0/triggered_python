
class Menu:
    """Menu Object representation"""

    def __init__(self, screen):
        self.screen = screen
        self.color = None
        self.image = None
        self.sprites = []

    def set_color(self, c):
        """Sets the background color of the menu"""
        self.color = c

    def set_image(self, img):
        """Sets the background image of the menu"""
        self.image = img

    def add(self, item):
        """Adds a drawable to the menu sprites"""
        self.sprites.append(item)

    def on_event(self, event):
        """Updates all the sprites in the menu group"""
        for sp in self.sprites:
            try:
                sp.on_event(event)
            except AttributeError:
                pass

    def draw(self):
        """Draws all the sprites in the menu group"""
        if self.color:
            self.screen.fill(self.color)
        if self.image:
            self.screen.blit(self.image, self.image.get_rect())
        for sp in self.sprites:
            sp.draw(self.screen)

    def update(self):
        """Updates all the sprites in the menu group"""
        for sp in self.sprites:
            try:
                sp.update()
            except AttributeError:
                pass
