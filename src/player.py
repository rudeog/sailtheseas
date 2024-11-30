# current player stats
from datetime import datetime, timedelta

from port import update_trading_post
from enum import Enum
from state import STARTING_DATE, MAX_LAST_VISITED, gs
from util import Direction, serialize_obj, deserialize_obj


class Player:
    class _state_e(Enum):
        NONE = 0
        ONLAND = 1
        ATSEA = 2

    # this handles simpler serialized types
    _serialized_attrs = ['name','birthplace','_days','_day_frags','_days_at_sea','_days_since_port',
                         '_doubloons', '_last_visited']

    def __init__(self):
        # player's personal info
        self.name: str = ""
        self.birthplace: str = ""

        # number of days sailing the seas
        self._days = 0
        self._day_frags = 0  # morning, afternoon, evening, night
        self._days_at_sea = 0  # how many days since left land
        self._days_since_port = 0 # how many days since landed at a port

        # last few islands visited
        self._last_visited = []
        # personal property
        self._doubloons = 0

        # whether docked or sailing or exploring, etc
        self._state = self._state_e.NONE

    def get(self):
        ret = serialize_obj(self)
        ret["s"] = self._state.value
        return ret

    def set(self, d: dict):
        self._state = self._state_e(d['s'])
        deserialize_obj(self, d)

    @property
    def num_days_elapsed(self):
        return self._days

    @property
    def num_days_at_sea(self):
        return self._days_at_sea

    @property
    def num_days_since_port(self):
        return self._days_since_port

    def time_increment(self) -> bool:
        """

        :return: true if one day has elapsed since last time increment
        """
        if self._day_frags == 3:
            self._days = self._days + 1
            self._day_frags = 0 # morning of the next day

            if self.is_at_sea():
                self._days_at_sea += 1
                self._days_since_port += 1

            return True
        else:
            self._day_frags = self._day_frags + 1

    @property
    def doubloons(self):
        return int(self._doubloons)

    def add_remove_doubloons(self, qty):
        self._doubloons += int(qty)
        if self._doubloons < 0:
            self._doubloons = 0
        return self._doubloons

    def current_date(self):
        return STARTING_DATE + timedelta(days=self._days)
    def current_time(self):
        return self._day_frags

    def is_at_sea(self):
        return self._state is self._state_e.ATSEA

    def is_on_land(self):
        return self._state is self._state_e.ONLAND

    def set_state_sailing(self):
        self._state=self._state_e.ATSEA

    def set_state_landed(self):
        self._state=self._state_e.ONLAND
        self._days_at_sea = 0
        p = gs.map.get_place_at_location(gs.ship.location)
        if p.island.port:
            self._days_since_port = 0


    def get_state_str(self):
        if self.is_on_land():
            return "on land"
        elif self.is_at_sea():
            return "aboard ship"
        else:
            return ""

    # add an island to lat visited. If this causes an island to
    # come off the list, then its trading data is updated
    def add_to_visited(self, island_id):
        # don't add it more than once
        if island_id in self._last_visited:
            return

        self._last_visited.append(island_id)
        if len(self._last_visited) > MAX_LAST_VISITED:
            r = self._last_visited[0]
            del self._last_visited[0]
            update_trading_post(r)


    def get_last_visited(self):
        return self._last_visited

class CrewMember:
    def __init__(self):
        self.name = ""
        self.role = ""
