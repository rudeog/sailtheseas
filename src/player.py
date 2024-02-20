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
        ONLAND = 1
        ATSEA = 2

    def __init__(self):
        # player's personal info
        self.name: str = ""
        self.birthplace: str = ""

        # number of days sailing the seas
        self._days = 0
        self._day_frags = 0  # morning, afternoon, evening, night

        # personal property
        self._doubloons = 0

        # whether docked or sailing or exploring, etc
        self._state = self._state_e.NONE

    def set(self, d: dict) -> bool:
        try:
            self.name = d['n']
            self.birthplace=d['bp']
            self._doubloons=d['d']
            self._state = self._state_e(d['s'])
            self._days = d['days']
            self._day_frags = d['frags']
        except KeyError:
            return False
        return True


    def get(self) -> dict:
        return {
            "n": self.name,
            "bp": self.birthplace,
            "d": self.doubloons,
            "s": self._state.value,
            "days": self._days,
            "frags": self._day_frags,
        }


    def num_days_elapsed(self):
        return self._days

    def time_increment(self):
        if self._day_frags == 3:
            self._days = self._days + 1
            self._day_frags = 0 # morning of the next day
        else:
            self._day_frags = self._day_frags + 1

    @property
    def doubloons(self):
        return self._doubloons

    def add_remove_doubloons(self, qty):
        self._doubloons += qty
        return self._doubloons

    def current_date(self):
        return STARTING_DATE + timedelta(days=self._days)
    def current_time(self):
        return self._day_frags

    def is_sailing(self):
        return self._state is self._state_e.ATSEA

    def is_onland(self):
        return self._state is self._state_e.ONLAND

    def set_state_sailing(self):
        self._state=self._state_e.ATSEA
    def set_state_landed(self):
        self._state=self._state_e.ONLAND


    def get_state_str(self):
        if self.is_onland():
            return "on land"
        elif self.is_sailing():
            return "aboard ship"
        else:
            return ""


class CrewMember:
    def __init__(self):
        self.name = ""
        self.role = ""
