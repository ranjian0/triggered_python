import math
import pymunk as pm
import itertools as it

from .entity import Entity
from core.math import Vec2
from resources import Resources
from core.physics import PhysicsWorld
from core.collection import Collection
from core.object import ProjectileCollection


RAYCAST_CATEGORY = 0x1
RAYCAST_FILTER = pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS ^ RAYCAST_CATEGORY)
def raycast(start, end):
    world = PhysicsWorld.instance
    return world.space.segment_query_first(start, end, 1, RAYCAST_FILTER)

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
        self.shape.filter = pm.ShapeFilter(categories=RAYCAST_CATEGORY)

        self.trigger_area = pm.Circle(self.body, 250)
        self.trigger_area.sensor = True
        self.trigger_area.color = (255, 0, 0, 100)
        PhysicsWorld.instance.add(self.trigger_area)
        PhysicsWorld.instance.register_collision(self.trigger_area.collision_type,
            on_enter=self.on_body_entered, on_exit=self.on_body_exited)


        # -- STATE MACHINE
        self._state = EnemyState_IDLE

        #XXX EnemyState_Idle
        self.idle_time = 0
        self.idle_wait_time = 3

        #XXX EnemyState_Patrol
        path = kwargs.get('waypoints')
        self.waypoints = it.cycle(path + path[::-1][1:-1])
        self.patrol_target = next(self.waypoints)
        self.patrol_epsilon = 10

        self.return_path = []
        self.return_target = None

        #XXX EnemyState_Chase
        self.chase_target = None
        self.chase_radius = self.trigger_area.radius * 1.25

        #XXX EnemyState_Attack
        self.projectiles = ProjectileCollection()
        self.attack_target = None
        self.attack_counter = 0
        self.attack_fequency = 10


    def new_state(self, state):
        if self._state:
            self._state.exit(self)
        self._state = state
        self._state.enter(self)

    def on_update(self, dt):
        Entity.on_update(self, dt)
        self._state.update(self, dt)
        self.projectiles.on_update(dt)

    def on_collision_enter(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            pass

        if hasattr(other, 'tag') and other.tag == 'PlayerBullet':
            self.damage(10)

    def on_body_entered(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            # -- check that the body is in our line of sight
            hit = raycast(self.position, other.position)
            visible = hit.shape in other.shapes
            if visible:
                self.chase_target = other
                self.new_state(EnemyState_CHASE)


    def on_body_exited(self, other):
        if hasattr(other, 'tag') and other.tag == 'Player':
            # No need to handle this, State only changes when we lose line of sight
            pass

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

    def _shoot_at(self, target):
        """ Eject projectile every attack frequency"""
        self.attack_counter += 1

        if self.attack_counter % self.attack_fequency == 0:
            # -- set relative muzzle location
            muzzle_loc = Vec2(self.radius*1.5, -self.radius*.4)

            # -- calculate direction of (1.muzzle location), (2.enemy rotation)
            rotation = muzzle_loc.angle + self.rotation
            d_muzzle = Vec2(math.cos(rotation), math.sin(rotation))
            d_enemy  = Vec2(math.cos(self.rotation), math.sin(self.rotation))

            # -- eject bullet
            pos = self.position + (d_muzzle * muzzle_loc.length)
            self.projectiles.add(pos, d_enemy, self.batch, tag="EnemyBullet")



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
        #XXX TODO
        # Calculate return path to waypoints if we cannot see patrol_target
        pass

    @staticmethod
    def update(enemy, dt):
        dist = enemy.position.get_dist_sqrd(enemy.patrol_target)
        if dist < enemy.patrol_epsilon:
            enemy.patrol_target = next(enemy.waypoints)

        enemy._look_at(enemy.patrol_target)
        enemy._move_to(enemy.patrol_target, dt)

    @staticmethod
    def exit(enemy):
        pass

class EnemyState_CHASE(EnemyState):
    """
    Move towards a chase target
        - If we get close enough, Transition to ATTACK
        - if target escapes (out of sight), Transition to PATROL
    """

    @staticmethod
    def enter(enemy):
        pass

    @staticmethod
    def update(enemy, dt):
        target = enemy.chase_target

        #XXX Check if target went out of sight
        hit = raycast(enemy.position, target.position)
        visible = hit.shape in target.shapes
        # -- still in our line of sight
        if visible:
            # Chase
            enemy._look_at(target.position)
            enemy._move_to(target.position, dt)

            # Attack if we are really close
            dist = enemy.position.get_dist_sqrd(target.position)
            if dist < (enemy.chase_radius**2)/2:
                enemy.attack_target = target
                enemy.new_state(EnemyState_ATTACK)


        # -- target escaped our sight
        else:
            enemy.new_state(EnemyState_PATROL)

    @staticmethod
    def exit(enemy):
        enemy.chase_target = None

class EnemyState_ATTACK(EnemyState):
    """
    Stop close to a target and shoot at it.
        - If target move away within (chase radius), Transition to CHASE
    """

    @staticmethod
    def enter(enemy):
        enemy.velocity = (0, 0)

    @staticmethod
    def update(enemy, dt):
        target = enemy.attack_target

        #XXX Check if target went out of sight
        hit = raycast(enemy.position, target.position)
        visible = hit.shape in target.shapes
        # -- still in our line of sight
        if visible:
            enemy._look_at(target.position)
            enemy._shoot_at(target.position)

            # -- Target moved away, Chase
            dist = enemy.position.get_dist_sqrd(target.position)
            if dist > (enemy.chase_radius**2)/2:
                enemy.chase_target = target
                enemy.new_state(EnemyState_CHASE)

        else:
            enemy.new_state(EnemyState_PATROL)

    @staticmethod
    def exit(enemy):
        enemy.attack_counter = 0
        enemy.attack_target = None
