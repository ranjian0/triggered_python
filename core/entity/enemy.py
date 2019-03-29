from .entity import Entity


class Enemy(Entity):

    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        self.direction = (0, 0)
        self.body.tag = "Enemy"
