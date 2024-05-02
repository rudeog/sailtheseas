from util import Direction, choices_ex, serialize_obj, deserialize_obj
from state import gs

wind_speeds = ['calm', 'light', 'moderate', 'strong']

class Wind:
    def __init__(self):
        self.direction = Direction('n')
        self.speed = 0

    def init_random(self):
        d = gs.rng_play.randint(0,7)
        self.direction = Direction(d)
        self.speed = choices_ex(gs.rng_play,[0,1,2,3],[1,4,6,4])

    def __str__(self):
        if self.speed == 0:
            return "calm"

        return f"{wind_speeds[self.speed]} from the {self.direction}"

    def set(self, d):
        self.speed = d["speed"]
        self.direction = Direction(d["dir"])

    def get(self):
        return {
            "speed": self.speed,
            "dir": self.direction.short()
        }


    def change_random(self):
        """
        Change wind randomly by up to 1 compass point mostly. may not change at all.
        In rare cases may change 3 compass points

        :return:
        """

        # calculate speed. weights are percentage chance
        self.speed = choices_ex(gs.rng_play,[0,1,2,3],[5,30,50,15])
        # one in 18 chances of being a rare event
        rare_event = choices_ex(gs.rng_play,[3,-3,0],[1,1,18])
        if rare_event:
            self.direction.add(rare_event)
        else:
            chg = gs.rng_play.randint(-1,1)
            self.direction.add(chg)

    def calc_speed_coeff(self, dir):
        """
        Given a direction that a body (ie the ship) is traveling, calculate the coefficient of speed
        for that body based on current wind speed and direction.

          - same direction as wind is blowing = 1.5
          - opposite direction as wind = 0.5
          - one point off same dir = 1.25
          - two points off same dir = 1.0 (will be same as 2 pts off opposite)
          - one point off opposite = 0.75
        - wind strength is a multiplier for directional value
          - none - no progress is made
          - light = 0.8
          - steady = 1.0
          - strong = 1.2
        - example: one point off same dir with strong wind = 1.25 * 1.2 = 1.5

        :param dir:
        :return:
        """
        coeff = 0.0

        # calc number of compas points difference between 2 directions
        # (ie how many points difference is the wind from the ship)
        if dir:
            points = dir.distance(self.direction)
        else:
            points = 1 # if dir is None it probably means we are navigating and already in the target square.
                         # will fix it one day so we can retain the direction. for now gloss over it
        # moving into the wind yields a lower value than moving away from it
        lu = [0.5,0.75,1.0,1.25,1.5]
        # exception here would indicate distance function is bad
        coeff = lu[points]

        # speed coefficient.
        slu = [0, 0.8, 1.0, 1.2]
        coeff *= slu[self.speed]

        return coeff