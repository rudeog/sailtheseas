# manages the map and each location in the map.
# a location has a populated bool which signifies whether anything is there

import random
from util import clamp
from names import PlaceGenerator

# number of chars for each location while dumping (may be overriden
# if total locations exceed 999)
PADDING = 3

# how densely to populate.
# higher is less dense
DENSITY_COEFF = 15


# a location within the map
class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.populated = False
        self.index = -1
        self.name: str = ""

    # set the location as being populated
    def set_place(self, idx):
        self.populated = True
        self.index = idx

    def dump(self, padding):
        if self.populated:
            v = f"{self.index}"
            vv = v.zfill(padding)
            return vv
        return " " * padding


class Map:
    def __init__(self, width, height, seed):
        if width < 10 or height < 10:
            raise Exception("invalid size. min is 10x10")

        self.cols: int = width
        self.rows: int = height
        self.seed: int = seed
        self.num_places: int = (width * height) // DENSITY_COEFF
        # initialize an empty map with given dimensions
        # row first then col
        self.map = [[Location(i, j) for i in range(self.cols)] for j in range(self.rows)]
        # we have an array of populated places
        self.places: list[Location] = []
        self._populate_map()
        self._define_places()

    def _populate_map(self):
        # populate with places
        # start in the middle
        x = self.cols // 2
        y = self.rows // 2
        self.map[y][x].set_place(0)
        self.places.append(self.map[y][x])
        # scatter the rest randomly
        random.seed(self.seed)
        for i in range(0, self.num_places - 1):
            x, y = self._get_validated_location()
            self.map[y][x].set_place(i + 1)
            self.places.append(self.map[y][x])

    # get a random x,y within the map
    def _get_random_location(self):
        return random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)

    def _get_all_nearby_places(self, x, y, count_only: bool = False, dist: int = 1):
        '''
        given a location returns a list of adjacent locations that are populated.
        :param x:
        :param y:
        :param count_only: just return a count instead of an array
        :param dist: how far out to look
        :return:
        '''

        ystart = clamp(y - dist, 0, self.rows - 1)
        yend = clamp(y + dist + 1, 0, self.rows)
        xstart = clamp(x - dist, 0, self.cols - 1)
        xend = clamp(x + dist + 1, 0, self.cols)

        adj = []
        count = 0
        for yy in range(ystart, yend):
            for xx in range(xstart, xend):
                if not (yy == y and xx == x) and self.map[yy][xx].populated:
                    if count_only:
                        count = count + 1
                    else:
                        adj.append(self.map[yy][xx])
        if count_only:
            return count
        return adj

    # get random location not adjacent to another filled location
    # will not make more than rows*cols attempts
    def _get_validated_location(self):
        t = self.rows * self.cols
        while t:
            x, y = self._get_random_location()

            if self.map[y][x].populated:  # don't populate same one twice
                continue
            count = self._get_all_nearby_places(x, y, True)
            if not count:
                return (x, y)
            t = t - 1
        raise Exception(f"failed to get validated location after {self.rows * self.cols} tries!")

    def get_nearby_places(self, place, min, max_dist):
        '''
        Get a list of places that are close to a given place. will start close and work outwards
        :param place_idx: place in question
        :param min: try to get a minimum of this amount
        :param max)distance: how many maximum spaces away in each direction to look
        :return: array of places. Empty set if no places within max_dist
        '''
        tmp = []
        for i in range(1, max_dist):
            a = self._get_all_nearby_places(place.x, place.y, False, i)
            if len(a) >= min:
                return a
            tmp = a
        return tmp

    def __str__(self):
        return self.render(0, 0, self.cols, self.rows)

    def render(self, xstart, ystart, xend, yend, override_fn=None):
        """
        Render the map or a portion of the map.
        :param xstart: left side start
        :param ystart: top side start
        :param xend: right side end
        :param yend:bottom side end
        :param override_fn: if specified, will call this function with each
               location, passing in the x and y of that location and will use
               the returned string for that location, unless its an empty string in
               which case it uses the default
        :return:
        """

        padding = max(PADDING, len(str(self.num_places)))
        parts = [" " * padding + " "]
        width = xend - xstart
        for i in range(xstart, xend):
            v = str(i).rjust(padding)
            parts.append(v)
        parts.append(f"\n")

        hdr = f"{' ' * padding}+{'-' * (width * padding)}+\n"
        parts.append(hdr)

        y = ystart
        for row in self.map[ystart:yend]:
            parts.append(str(y).rjust(padding) + "|")
            for item in row[xstart:xend]:
                overriden = ""
                if override_fn:  # override function should return a non-empty string to override this location
                    overriden = override_fn(item.x, item.y)
                if overriden:
                    parts.append(overriden.rjust(padding))
                else:
                    parts.append(f"{item.dump(padding)}")
            parts.append("|\n")
            y = y + 1
        parts.append(hdr)
        return "".join(parts)

    def _define_places(self):
        ng = PlaceGenerator(self.seed)
        for loc in self.places:
            loc.name = ng.name()

# number of spaces to move to get between 2 points assuming moving
# diagonal counts as one move
def distance_between_points(x1, y1, x2, y2):
    horz = abs(x2 - x1)
    vert = abs(y2 - y1)
    # min covers the diagonal movement, abs covers the remaining spaces
    return min(vert, horz) + abs(vert - horz)


# function to print a ship at a specific location
def generate_function(x, y):
    def inner_function(xx, yy):
        if xx == x and yy == y:
            return "{_}"
        else:
            return ""

    return inner_function


if __name__ == "__main__":
    world = Map(60, 25, 13)
    print(world)
    print(f"total places {world.num_places}")
    r = world.get_nearby_places(world.places[0], 4, 5)
    for p in r:
        print(p.index)
    sub = world.render(24, 8, 44, 18, generate_function(36, 10))
    print(sub)
    sub = world.render(27, 16, 28, 17)
    print(sub)
