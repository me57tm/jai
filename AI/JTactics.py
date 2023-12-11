import plus
import AI
from AI import vector3
import Arenas
import math
import random
import time


class JCharge(AI.Tactic):
    name = "JCharge"

    def __init__(self, ai):
        AI.Tactic.__init__(self, ai)

        self.regroupPos = None
        self.regroupDir = True
        self.regroupTime = 0

    def Evaluate(self):
        self.priority = 0
        self.target_id, range = self.ai.GetNearestEnemy()

        if self.target_id != None:
            heading = self.ai.GetHeadingToID(self.target_id, False)

            # no turning = more desirable
            self.priority = 100 - (abs(heading) * 20)

            # too close to enemy = less desirable
            if range < 3: self.priority -= 75 * (3 - range)

            clear_path = self.ai.IsStraightPathClear(self.ai.GetLocation(), plus.getLocation(self.target_id))
            if not clear_path: self.priority -= 75

    def Execute(self):
        if self.target_id != None:
            self.ai.enemy_id = self.target_id

            # default turning & throttle off
            self.ai.Throttle(0)
            self.ai.Turn(0)

            heading = self.ai.GetHeadingToID(self.target_id, False)
            target_loc = plus.getLocation(self.target_id)
            clear_path = self.ai.IsStraightPathClear(self.ai.GetLocation(), target_loc)

            distance = (vector3(target_loc) - vector3(self.ai.GetLocation())).length()
            speed = self.ai.GetSpeed()

            # if we're close but not moving very fast, pick a new location and back toward it
            if (distance < 3 and speed < 2.0) or (distance < 5 and speed < 0):
                if self.regroupPos == None or self.regroupTime <= 0:
                    self.regroupPos = None
                    # pick a point near us that has a clear shot at the target?
                    for r in (0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6):
                        angle = self.ai.GetHeading(True) + r * (math.pi / 6)
                        new_dir = vector3(math.sin(angle), 0, math.cos(angle))
                        dest = vector3(target_loc) + new_dir * 5

                        clear_path = self.ai.IsStraightPathClear(dest.asTuple(), target_loc)
                        if clear_path:
                            self.regroupPos = dest.asTuple()
                            self.regroupDir = (abs(r) <= 3)
                            self.regroupTime = 16
                            break

                # sanity check: if we can't find a valid position, drive forward or backward
                if self.regroupPos == None:
                    self.regroupDir = not self.regroupDir
                    range = 5
                    if self.regroupDir: range = -5
                    self.regroupPos = (
                                vector3(self.ai.GetLocation()) + vector3(self.ai.GetDirection()) * range).asTuple()
                    self.regroupTime = 16

                self.ai.DriveToLocation(self.regroupPos, self.regroupDir)
                self.regroupTime -= 1
            elif distance > 3 and abs(heading) > .35 or not clear_path:
                # if we don't have a clear shot, get closer
                self.ai.DriveToLocation(plus.getLocation(self.target_id))
            else:
                # drive as fast as we can toward the target
                self.ai.AimToHeading(heading)
                self.ai.Throttle(100)
                self.regroupPos = None

            return True
        else:
            return False

class Chaos(AI.Tactic):
    name = "Chaos"

    def __init__(self, ai):
        AI.Tactic.__init__(self, ai)
        self.timer = 0
        self.loc = (0,0,0)
        self.target_id = self.ai.GetNearestEnemy()

    def Evaluate(self):
        self.priority = 150
        self.target_id = self.ai.GetNearestEnemy()

    def Execute(self):
        self.ai.Throttle(0)
        self.ai.Turn(0)
        if self.timer == 0:
            #self.loc = vector3(random.randint(0, 20), 0, random.randint(0, 20)).asTuple()
            #self.loc = plus.getLocation(self.ai.GetNearestEnemy()).asTuple()
            plus.emitSmoke(30, self.loc, (0, 2, 0), (3, 3, 3))
            self.ai.DriveToLocation(plus.getLocation(self.target_id))
            self.timer = 10
        else:
            plus.emitSmoke(30, self.loc, (0, 2, 0), (3, 3, 3))
            self.timer -= 1
        return True


class Push(AI.Tactic):
    name = "Push"

    def __init__(self, ai):
        AI.Tactic.__init__(self, ai)
        self.hazard_location = None
        self.enemy_location = None
        self.enemy_to_hazard = None
        self.to_hazard = None

    def Evaluate(self):
        # should be used when close to opponent, and we want to push them into a hazard, also if
        a = Arenas.currentArena
        self.target_id, e_range = self.ai.GetNearestEnemy()
        self.hazard_location = None
        enemy_loc = plus.getLocation(self.target_id)
        hazard = a.GetNearestHazard(enemy_loc)
        if hazard is None:
            self.priority = -100
        else:
            # self.priority = 100
            self.hazard_location = hazard.location
            self.enemy_location = vector3(plus.getLocation(self.target_id))
            dest = vector3(self.hazard_location)
            self.enemy_to_hazard = dest - self.enemy_location
            self.enemy_to_hazard.y = 0
            self.to_hazard = dest - vector3(self.ai.GetLocation())
            self.to_hazard.y = 0
            heading_to_enemy = self.ai.GetHeadingTo(self.enemy_location.asTuple(), False)
            heading_to_hazard = self.ai.GetHeadingTo(self.to_hazard.asTuple(), False)
            if abs(heading_to_enemy - heading_to_hazard) < math.pi / 3:
                self.priority = 100 - (95 * abs(heading_to_enemy - heading_to_hazard))
            else:
                self.priority = 10 * abs(heading_to_enemy - heading_to_hazard)
            # if the enemy is further than us from the nearest hazard, try to get to the back of the robot using the Shove Tactic
            if self.to_hazard.length() < self.enemy_to_hazard.length():
                self.priority -= 90
            # penalty for distance
            self.priority -= math.pow(1.5, e_range)

    def Execute(self):
        if self.hazard_location and self.target_id != None:
            # If the ai is too close to a hazard, don't push and just aim towards the hazard to keep the opponent pushed onto it. To prevent self-inflicted damage
            if self.to_hazard.length() < 3:
                plus.emitSmoke(30, (0, 0, 0), (0, 2, 0), (3, 3, 3))
                self.ai.AimToHeading(self.ai.GetHeadingTo(self.to_hazard.asTuple(), False))
                return False

            self.ai.enemy_id = self.target_id
            # Try and target a point between the nearest hazard and the enemy
            target = self.enemy_to_hazard
            target = target.normalize()
            # target += self.to_hazard * 0.5
            target += self.enemy_location

            if not self.ai.IsStraightPathClear(self.enemy_location.asTuple(), target.asTuple()):
                target = self.enemy_location

            plus.emitSmoke(30, target.asTuple(), (0, 2, 0), (3, 3, 3))
            h = self.ai.GetHeadingTo(target.asTuple(), False)
            self.ai.AimToHeading(h)
            if abs(h) < 0.3:
                throttle_amount = 100 * self.enemy_to_hazard.length()
                if throttle_amount > 100: throttle_amount = 100
                self.ai.Throttle(throttle_amount)
            # self.ai.AimToHeading(h)
            return True
        else:
            return False
