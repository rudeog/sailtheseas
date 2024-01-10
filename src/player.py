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
        return f"The {current_date.day}{ordinal_suffix(current_date.day)} of {current_date.strftime('%B')} {current_date.year}"

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


class Ship:
    def __init__(self):
        self.name = ""
        self.cargo: CargoCollection = CargoCollection()
        self.location: tuple = (-1, -1)

        # if sailing in a direction this will have it
        self.direction: Direction = None
        # if sailing and we have a target location
        self.target: tuple = (-1, -1)
        # what percentage of the current location we've travelled
        self.travel_pct = 0

    def reset_bearing(self):
        self.direction = None
        self.target = (-1, -1)
        self.travel_pct = 0

    def have_bearing(self):
        if self.direction is None and self.target == (-1, -1):
            return False
        return True
