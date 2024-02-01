from cargo import CargoCollection
from enum import Enum

from state import gs, DEFAULT_CARGO_CAPACITY
from util import Direction, add_pair

_SHORT_RADIUS = 30  # distance from left, right, top or bottom edge to center of square
_DIAG_EXTRA = 12  # extra distance for diagonal travel (short radius * square root of 2 is the total long radius)


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
        self.cargo_capacity = DEFAULT_CARGO_CAPACITY
        self.miles_traveled = 0
        self.cargo: CargoCollection = CargoCollection()
        self._location: tuple = (-1, -1)

        # if sailing we might have a dir/target
        self.b: Bearing = Bearing()

        # we are either moving toward center of square or away from center
        self._toward_center = False

        # nautical miles traveled from either center, or edge
        self._miles_traveled_in_square = 0

        # will be true if we entered the square from a corner. there are 42 miles to center
        # from a corner, but only 30 miles from a vertical/horizontal entry. we always take 30
        # miles from center to edge, so we need to add the extra 12 miles when entering from a diagonal, so
        # if coming in from a diagonal it will be 54 miles
        self._diagonal_entry = False

    @property
    def location(self):
        return self._location

    def set_location(self, location: tuple[int, int]):
        """
        set ship to a specific location. will be centered at that location
        :param location:
        :return:
        """
        self._location = location
        self._toward_center = False
        self._miles_traveled_in_square = 0
        self._diagonal_entry = False

    def distance_to_location(self, location: tuple[int, int]):
        """
        Returns the number of miles it would take to sail to a location
        :param location:
        :return:
        """
        if location == self._location:  # in same square
            dist = self._distance_to_center()  # miles to center of our own square
        else:
            dist = distance_between_points(self._location, location)
            if self._toward_center:  # we must move to center before moving away
                dist += self._distance_to_center()
            else:  # we are moving away, so we can credit that against or distance
                dist -= self._miles_traveled_in_square
        return dist

    def _distance_to_center(self):
        """
        Distance in miles to center of current square from current location. Whether moving
        toward or away
        :return:
        """
        if not self._toward_center:  # this would be if you now targeted the current square
            return self._miles_traveled_in_square

        dist_to_center = self._distance_from_edge_to_center()
        return dist_to_center - self._miles_traveled_in_square

    def _distance_from_edge_to_center(self):
        """
        Total distance to travel to either edge or center 
        :return: 
        """
        dist = _SHORT_RADIUS
        if self._diagonal_entry:
            dist += (_DIAG_EXTRA * 2)
        return dist

    SAIL_RESULT_ARRIVED = 1  # arrived at a set target
    SAIL_RESULT_EDGE_OF_WORLD = 2  # reached edge of world (bearing is reset)
    SAIL_RESULT_ENTERED_NEW_SQUARE = 3  # ended up in a new square from this sail action

    def sail(self, miles_available) -> tuple[int, int]:
        """
        Sail the ship
        :param miles_available: how many miles to allow sailing
        :return: one of the SAIL_RESULT codes and number of miles that were travelled
        """
        # 60 miles is the distance of one square horizontal or vertical.
        # 85 miles is the diagonal distance
        # so 30 miles from left/right/up/down to center and 42 miles from diagonal
        # we only count diagonal miles when traveling TO center. It is more difficult for traveling away,
        # because if they shift directions while traveling from a diagonal to a non-diagonal. Therefore
        # when entering from diagonal we add these extra miles on. Normally it would be 42 miles from diagonal
        # to center, so we make it 54 miles = 30 + ( (42-30) * 2  )
        arrived = False  # will be set to true if we are navigating and reach our dest
        hit_edge = False  # will be set to true if we hit the edge of the world
        new_location = False  # we entered a new location
        orig_miles = miles_available
        # there is an edge case where we are moving away from center, but we are now navigating to that center.
        # eg we reached center, passed it, are on the same square and now have nav set to that square
        if self.b.is_target() and self.b.get() == self._location and not self._toward_center:
            # diagonal will be false here because we are moving away from center
            self._miles_traveled_in_square = _SHORT_RADIUS - self._miles_traveled_in_square
            self._toward_center = True

        while miles_available:  # chew thru miles until we have exhausted them or reached a target

            dist_to_center = self._distance_from_edge_to_center()
            to_target = dist_to_center - self._miles_traveled_in_square

            if miles_available < to_target:  # just advance toward center or edge
                self._miles_traveled_in_square += miles_available
                self.miles_traveled += miles_available
                miles_available=0
                break
            else:  # we have enough miles to reach the center, or the edge of a square
                miles_available -= to_target
                self.miles_traveled += to_target
                self._miles_traveled_in_square = 0
                if self._toward_center:
                    # reached center, so start moving away from center next
                    self._toward_center = False
                    self._diagonal_entry = False
                    if self.b.is_target() and self._location == self.b.get():
                        # throw away rest of miles we are done navigating to target
                        arrived = True
                        break
                else:  # reached edge of square so move to next square
                    self._toward_center = True
                    # we move to a new square or hit the edge
                    if self.b.is_direction():
                        coords = self.b.get().to_coords()
                    else:
                        coords = get_step_towards_destination(self._location, self.b.get())
                    # if both are either 1 or -1 we are entering on a diagonal and must travel further
                    # to get to center of the new square
                    is_diagonal = (coords[0] and coords[1])
                    self._diagonal_entry = is_diagonal
                    new_coords = add_pair(self._location, coords)
                    loc = gs.map.get_location(new_coords)
                    if loc:
                        self._location = new_coords
                        loc.visited = True
                        new_location = True
                    else:  # hit edge so throw away rest of miles
                        hit_edge = True
                        break
        if arrived:
            return self.SAIL_RESULT_ARRIVED, orig_miles-miles_available
        if hit_edge:
            return self.SAIL_RESULT_EDGE_OF_WORLD, orig_miles-miles_available
        if new_location:
            return self.SAIL_RESULT_ENTERED_NEW_SQUARE, orig_miles-miles_available
        return 0,orig_miles-miles_available

    def describe(self):
        wt = int(self.cargo.total_weight()/2000)
        gs.output(f"{self.name} is a merchant ship that has a cargo capacity of {int(self.cargo_capacity/2000)} tons. "
              f"It has traveled {self.miles_traveled} nautical miles in the seas of {gs.world_name}. "
              f"It is currently carrying cargo to the weight of approximately {wt} tons.")

    def debug_prompt(self):
        p = f"\n{'inward' if self._toward_center else 'outward'} {self._miles_traveled_in_square} miles"
        if self._diagonal_entry:
            p = p + " diagonal"
        return p


# number of miles to move to get between 2 points assuming moving
# diagonal counts as one move. This assumes moving from center of point a to center of point b
def distance_between_points(a: tuple[int, int], b: tuple[int, int]):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    horz = abs(x2 - x1)
    vert = abs(y2 - y1)

    diags = min(vert, horz)
    nondiags = abs(vert - horz)

    return (diags * (_SHORT_RADIUS + _DIAG_EXTRA) * 2) + (nondiags * _SHORT_RADIUS * 2)


def get_step_towards_destination(coord1, coord2):
    # Calculate the differences between corresponding points and
    # return what would be a single step toward that goal
    xdiff = coord2[0] - coord1[0]
    ydiff = coord2[1] - coord1[1]
    if xdiff:
        xdiff = -1 if xdiff < 0 else 1
    if ydiff:
        ydiff = -1 if ydiff < 0 else 1
    return xdiff, ydiff
