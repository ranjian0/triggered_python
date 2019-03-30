from .entity import Entity
from resources import Resources


class Enemy(Entity):

    def __init__(self, **kwargs):
        Entity.__init__(self, image=Resources.instance.sprite("robot1_gun"), **kwargs)
        self.direction = (0, 0)
        self.body.tag = "Enemy"

    def on_collision_enter(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            pass
