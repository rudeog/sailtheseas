# current player stats
from datetime import datetime, timedelta

from cargo import CargoCollection
from enum import Enum

from util import Direction

# when our game starts
STARTING_DATE = date_constant = datetime(1716, 6, 1)


class Player:
    class _state_e(Enum):
        NONE = 0
        DOCKED = 1
        EXPLORING = 2
        SAILING = 3

    def __init__(self):
        # player's personal info
        self.name: str = ""
        self.birthplace: str = ""

        # number of days sailing the seas
        self._days = 0
        self._day_frags = 0  # morning, afternoon, evening, night

        # personal property
        self.doubloons = 10

        # whether docked or sailing or exploring, etc
        self._state = self._state_e.NONE

    def num_days_elapsed(self):
        return self._days

    def time_increment(self):
        if self._day_frags == 3:
            self._days = self._days + 1
            self._day_frags = 0 # morning of the next day
        else:
            self._day_frags = self._day_frags + 1

    def current_date(self):
        return STARTING_DATE + timedelta(days=self._days)
    def current_time(self):
        return self._day_frags

    def is_sailing(self):
        return self._state is self._state_e.SAILING

    def is_docked(self):
        return self._state is self._state_e.DOCKED

    def is_exploring(self):
        return self._state is self._state_e.EXPLORING

    def has_state(self): # should always have state
        return self._state is not self._state_e.NONE

    def set_state_sailing(self):
        self._state=self._state_e.SAILING
    def set_state_docked(self):
        self._state=self._state_e.DOCKED
    def set_state_exploring(self):
        self._state=self._state_e.EXPLORING


    def get_state_str(self):
        if self.is_docked():
            return "docked"
        elif self.is_exploring():
            return "exploring"
        elif self.is_sailing():
            return "aboard ship"
        else:
            return ""


class CrewMember:
    def __init__(self):
        self.name = ""
        self.role = ""
