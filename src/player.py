# current player stats
from datetime import datetime, timedelta

from cargo import CargoCollection
from enum import Enum

from util import Direction


class PlayerState(Enum):
    NONE = 0
    DOCKED = 1
    EXPLORING = 2
    SAILING = 3


# when our game starts
STARTING_DATE = date_constant = datetime(1716, 6, 1)


class Player:
    def __init__(self):
        # player's personal info
        self.name: str = ""
        self.birthplace: str = ""

        # players ship
        self.ship: Ship = Ship()

        # number of days sailing the seas
        self.days = 0

        # personal property
        self.doubloons = 10

        # whether docked or sailing or exploring, etc
        self.state = PlayerState.NONE

    def game_date(self):
        def ordinal_suffix(day):
            if 10 <= day % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            return suffix
        current_date = STARTING_DATE + timedelta(days=self.days)
        return f"{current_date.day}{ordinal_suffix(current_date.day)} of {current_date.strftime('%B')} {current_date.year}"

    def get_state(self):
        if self.state is PlayerState.DOCKED:
            return "docked"
        elif self.state is PlayerState.EXPLORING:
            return "exploring"
        elif self.state is PlayerState.SAILING:
            return "sailing"
        else:
            return ""

class CrewMember:
    def __init__(self):
        self.name = ""
        self.role = ""

class Bearing:
    class Type(Enum):
        NONE = 0
        DIRECTION = 1,
        TARGET = 2

    def __init__(self):
        self.type = self.Type.NONE
        self.direction = None
        self.target = (-1,-1)
    def reset(self):
        self.type = self.Type.NONE
        self.direction = None
        self.target = (-1,-1)
    def is_set(self):
        return self.type is not self.Type.NONE

    def get(self):
        second = None
        if self.type is self.Type.TARGET:
            second = self.target
        if self.type is self.Type.DIRECTION:
            second = self.direction
        return self.type, second
    def set_direction(self, dir: Direction):
        self.direction=dir
        self.target=(-1,-1)
        self.type = self.Type.DIRECTION
    def set_target(self, target: tuple[int,int]):
        self.target=target
        self.direction=None
        self.type = self.Type.TARGET



class Ship:
    def __init__(self):
        self.name = ""
        self.cargo: CargoCollection = CargoCollection()
        self.location: tuple = (-1, -1)

        # if sailing we might have a dir/target
        self.bearing: Bearing = Bearing()

        # what percentage of the current location we've travelled
        self.travel_pct = 0
