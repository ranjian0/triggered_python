import pymunk as pm
from .entity import Entity
from resources import Resources
from core.physics import PhysicsWorld


class Enemy(Entity):

    def __init__(self, **kwargs):
        Entity.__init__(self, image=Resources.instance.sprite("robot1_gun"), **kwargs)
        self.direction = (0, 0)
        self.body.tag = "Enemy"

        self.trigger_area = pm.Circle(self.body, 250)
        self.trigger_area.sensor = True
        self.trigger_area.color = (255, 0, 0, 100)
        PhysicsWorld.instance.add(self.trigger_area)
        PhysicsWorld.instance.register_collision(self.trigger_area.collision_type,
            on_enter=self.on_body_entered, on_exit=self.on_body_exited)

        self._state = None
        self.new_state(EnemyState_IDLE)

    def new_state(self, state):
        if self._state:
            self._state.exit(self)
        self._state = state
        self._state.enter(self)

    def on_update(self, dt):
        Entity.on_update(self, dt)
        self._state.update(self, dt)

    def on_collision_enter(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            pass

        if hasattr(other, 'tag') and other.tag == 'PlayerBullet':
            pass

    def on_body_entered(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            pass

    def on_body_exited(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            pass


class EnemyState:
    """ Base class for Enemy States """

    @staticmethod
    def enter(enemy):
        return NotImplementedError()

    @staticmethod
    def update(enemy, dt):
        return NotImplementedError()

    @staticmethod
    def exit(enemy):
        return NotImplementedError()


class EnemyState_IDLE(EnemyState):
    """
    Initial state for the enemy:
        - Do nothing
        - Transition to PATROL
    """

    @staticmethod
    def enter(enemy):
        enemy.new_state(EnemyState_PATROL)

    @staticmethod
    def update(enemy, dt):
        pass

    @staticmethod
    def exit(enemy):
        pass

class EnemyState_PATROL(EnemyState):
    """
    Move enemy through navigation path
        - If player comes within trigger_area, Transition to CHASE
    """

    @staticmethod
    def enter(enemy):
        pass

    @staticmethod
    def update(enemy, dt):
        pass

    @staticmethod
    def exit(enemy):
        pass

class EnemyState_CHASE(EnemyState):
    """
    Move towards a chase target
        - If we get close enough (attack radius), Transition to ATTACK
        - if target escapes, Transition to PATROL
    """

    @staticmethod
    def enter(enemy):
        pass

    @staticmethod
    def update(enemy, dt):
        pass

    @staticmethod
    def exit(enemy):
        pass

class EnemyState_ATTACK(EnemyState):
    """
    Stop close to a target and shoot at it.
        - If target move away within (chase radius), Transition to CHASE
    """

    @staticmethod
    def enter(enemy):
        pass

    @staticmethod
    def update(enemy, dt):
        pass

    @staticmethod
    def exit(enemy):
        pass
