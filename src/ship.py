from cargo import CargoCollection
from enum import Enum
from util import Direction


class Bearing:
    """
    Represents the ship's bearing which can either be none, sailing in a direction,
    or navigating to a Location
    """

    class _type_e(Enum):
        NONE = 0
        DIRECTION = 1,
        TARGET = 2

    def __init__(self):
        self._type = self._type_e.NONE
        self._direction = None
        self._target = (-1, -1)

    def reset(self):
        """
        Clear bearing
        :return:
        """
        self._type = self._type_e.NONE
        self._direction = None
        self._target = (-1, -1)

    def is_set(self):
        """
        check if navigating or directioning
        :return:
        """
        return self._type is not self._type_e.NONE

    def is_direction(self):
        return self._type is self._type_e.DIRECTION

    def is_target(self):
        return self._type is self._type_e.TARGET

    def get(self):
        if self._type is self._type_e.TARGET:
            return self._target
        if self._type is self._type_e.DIRECTION:
            return self._direction
        return None

    def set_direction(self, dir: Direction):
        self._direction = dir
        self._target = (-1, -1)
        self._type = self._type_e.DIRECTION

    def set_target(self, target: tuple[int, int]):
        self._target = target
        self._direction = None
        self._type = self._type_e.TARGET


class Ship:
    def __init__(self):
        self.name = ""
        self.cargo: CargoCollection = CargoCollection()
        self.location: tuple = (-1, -1)

        # if sailing we might have a dir/target
        self.b: Bearing = Bearing()

        # we are either moving toward center of square or away from center
        self.toward_center = False

        # nautical miles traveled from either center, or edge
        self.miles_traveled_in_square = 0

        # will be true if we entered the square from a corner. there are 42 miles to center
        # from a corner, but only 30 miles from a vertical/horizontal entry
        self.diagonal_entry = False

