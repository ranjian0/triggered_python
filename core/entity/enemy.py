import pymunk as pm
from .entity import Entity
from resources import Resources
from core.physics import PhysicsWorld


class Enemy(Entity):

    def __init__(self, **kwargs):
        Entity.__init__(self, image=Resources.instance.sprite("robot1_gun"), **kwargs)
        self.direction = (0, 0)
        self.body.tag = "Enemy"

        self.trigger_area = pm.Circle(self.body, 100)
        self.trigger_area.sensor = True
        self.trigger_area.color = (255, 0, 0, 100)
        PhysicsWorld.instance.add(self.trigger_area)
        PhysicsWorld.instance.register_collision(self.trigger_area.collision_type,
            on_enter=self.on_body_entered, on_exit=self.on_body_exited)

    def on_collision_enter(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            pass

        if hasattr(other, 'tag') and other.tag == 'PlayerBullet':
            # -- prevent enemy from being pushed by bullet
            self.velocity = (0, 0)

    def on_body_entered(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            print("Player is around")

    def on_body_exited(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            print("Player ran escaped")