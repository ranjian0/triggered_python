import math
import pymunk as pm
import itertools as it

from .entity import Entity
from core.math import Vec2
from resources import Resources
from core.physics import PhysicsWorld
from core.collection import Collection

def EnemyCollection(positions, waypoints):
    col = Collection(Enemy)
    col.add_many(len(positions), position=positions, waypoints=waypoints)
    return col

class Enemy(Entity):

    def __init__(self, **kwargs):
        Entity.__init__(self, image=Resources.instance.sprite("robot1_gun"), **kwargs)
        self.speed = 175
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

        # -- State Machine Properties
        #XXX EnemyState_Idle
        self.idle_time = 0
        self.idle_wait_time = 5

        #XXX EnemyState_Patrol
        path = kwargs.get('waypoints')
        self.waypoints = it.cycle(path + path[::-1][1:-1])
        self.patrol_target = next(self.waypoints)
        self.patrol_epsilon = 10

        self.return_path = []
        self.return_target = None

        #XXX EnemyState_Chase
        self.chase_target = None

        #XXX EnemyState_Attack
        self.attack_target = None
        self.attack_fequency = 10


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
            self.damage(10)

    def on_body_entered(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            self.chase_target = other

    def on_body_exited(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            self.chase_target = None

    def _look_at(self, target):
        tx, ty = target
        px, py = self.position
        self.rotation = math.atan2(ty-py, tx-px)

    def _move_to(self, target, dt):
        diff = Vec2(target) - self.position
        dist = self.position.get_dist_sqrd(target)
        if dist:
            dx, dy = diff.normalized()
            self.velocity = (
                dx * self.speed * dt,
                dy * self.speed * dt)
        else:
            self.velocity = (0, 0)



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
        - Wait for idle_wait time
        - Transition to PATROL
    """

    @staticmethod
    def enter(enemy):
        pass

    @staticmethod
    def update(enemy, dt):
        enemy.idle_time += dt
        if enemy.idle_time >= enemy.idle_wait_time:
            enemy.new_state(EnemyState_PATROL)

    @staticmethod
    def exit(enemy):
        enemy.idle_time = 0

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
        dist = enemy.position.get_dist_sqrd(enemy.patrol_target)
        if dist < enemy.patrol_epsilon:
            enemy.patrol_target = next(enemy.waypoints)

        enemy._look_at(enemy.patrol_target)
        enemy._move_to(enemy.patrol_target, dt)

        if enemy.chase_target:
            enemy.new_state(EnemyState_CHASE)

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
