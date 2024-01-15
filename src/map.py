# manages the map and each location in the map.
# a location has a populated bool which signifies whether anything is there

import random
from util import clamp
from names import PlaceGenerator, NameGenerator
from port import Port

# number of chars for each location while dumping (may be overriden
# if total locations exceed 999)
PADDING = 3

# how densely to populate.
# higher is less dense
DENSITY_COEFF = 15

PORT_PROBABILITY = 75.0

INCLUDE_XY_RULER=True

# for local map render, how many spaces in each dir
LOCAL_VIEW_SIZE = 2

# a location within the map
class Location:
    def __init__(self, x, y):
        self.location = (x, y)
        self.populated = False
        self.visited = False
        self.index = -1
        self.name: str = ""
        self.port = None

    # set the location as being populated
    def set_place(self, idx):
        self.populated = True
        self.index = idx

    def dump(self, padding, visited_only):
        if self.populated:
            if (visited_only and self.visited) or not visited_only:
                v = f"{self.index}"
                vv = v.center(padding)
                return vv
        if self.visited:
            return ".".center(padding)
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

    def get_place_by_index(self, index: int):
        if index <0 or index >= len(self.places):
            return None
        return self.places[index]

    def get_location(self, coords:tuple[int,int]):
        """
        Return a location at given coordinates. if invalid return None
        :param coords: 
        :return: 
        """
        if coords[0] < 0 or coords[1] < 0 or coords[0] >= self.rows or coords[1] >= self.cols:
            return None
        y=coords[1]
        x=coords[0]
        return self.map[y][x]

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

    def get_all_nearby_places(self, location: tuple[int, int], count_only: bool = False, dist: int = LOCAL_VIEW_SIZE):
        '''
        given a location returns a list of adjacent locations that are populated.
        :param x:
        :param y:
        :param count_only: just return a count instead of an array
        :param dist: how far out to look
        :return:
        '''
        y = location[1]
        x = location[0]
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
            count = self.get_all_nearby_places((x, y), True, 1)
            if not count:
                return (x, y)
            t = t - 1
        raise Exception(f"failed to get validated location after {self.rows * self.cols} tries!")

    def get_place_at_location(self, location: tuple[int, int]):
        """
        Get a place at a location. return None if there isnt any
        :return:
        """
        for p in self.places:
            if p.location == location:
                return p
        return None

    def unused_get_nearby_places(self, location: tuple[int, int], min, max_dist = LOCAL_VIEW_SIZE):
        '''
        Get a list of places that are close to a given location. will start close and work outwards
        :param location: the x/y location
        :param min: try to get a minimum of this amount
        :param max)distance: how many maximum spaces away in each direction to look
        :return: array of places. Empty set if no places within max_dist
        '''
        tmp = []
        for i in range(1, max_dist):
            a = self.get_all_nearby_places(location, False, i)
            if len(a) >= min:
                return a
            tmp = a
        return tmp

    def __str__(self):
        return self.render(0, 0, self.cols, self.rows)

    def render(self, xstart, ystart, xend, yend, override_fn=None, visited_only=False):
        """
        Render the map or a portion of the map.
        :param xstart: left side start
        :param ystart: top side start
        :param xend: right side end inclusive
        :param yend:bottom side end inclusive
        :param override_fn: if specified, will call this function with each
               location, passing in the x and y of that location and will use
               the returned string for that location, unless its an empty string in
               which case it uses the default
        :return:
        """

        ystart = clamp(ystart, 0, self.rows - 1)
        yend = clamp(yend+1, 0, self.rows)
        xstart = clamp(xstart, 0, self.cols - 1)
        xend = clamp(xend+1, 0, self.cols)

        padding = max(PADDING, len(str(self.num_places)))
        width = xend - xstart
        if INCLUDE_XY_RULER:
            parts = [" " * padding + " "]

            for i in range(xstart, xend):
                v = str(i).rjust(padding)
                parts.append(v)
            parts.append(f"\n")
            hdr = f"{' ' * padding}"
        else:
            parts=[]
            hdr=""
        hdr=hdr+f"+{'-' * (width * padding)}+\n"

        parts.append(hdr)

        y = ystart
        for row in self.map[ystart:yend]:
            if INCLUDE_XY_RULER:
                rh = str(y).rjust(padding)
            else:
                rh = ""
            parts.append(rh + "|")
            for item in row[xstart:xend]:
                overriden = ""
                if override_fn:  # override function should return a non-empty string to override this location
                    overriden = override_fn(item.location)
                if overriden:
                    parts.append(overriden.rjust(padding))
                else:
                    parts.append(f"{item.dump(padding, visited_only)}")
            parts.append("|\n")
            y = y + 1
        parts.append(hdr)
        return "".join(parts)

    def _define_places(self):
        pg = PlaceGenerator(self.seed)
        ng = NameGenerator(self.seed)
        first=True # we always want a port at the first location
        for loc in self.places:
            loc.name = pg.name()
            if first or random.random() < PORT_PROBABILITY / 100.0:
                # has a port
                if random.random() < .4:
                    # use a name rather than a place
                    port_name = "Port " + ng.name().last
                else:
                    port_name = str(pg.name()) + " Harbor"
                loc.port = Port(port_name)
            first=False


    # render local area which includes islands that are nearby even if not visited
    def render_local(self, my_loc: tuple[int,int] ):
        # get bounding area
        xstart = max(my_loc[0]-LOCAL_VIEW_SIZE,0)
        ystart = max(my_loc[1]-LOCAL_VIEW_SIZE,0)
        xend = min(my_loc[0]+LOCAL_VIEW_SIZE, self.cols)
        yend = min(my_loc[1]+LOCAL_VIEW_SIZE, self.rows)

        nearby = self.get_all_nearby_places(my_loc)
        legend = self._render_legend(my_loc, nearby)
        me = self.get_place_at_location(my_loc)
        if me:
            fill = '*'
        else:
            fill = '.'
        ret_map = self.render(xstart,ystart,xend,yend,generate_ship_function(my_loc, fill))
        return ret_map + legend

    def _render_legend(self, my_loc, nearby=None):
        if nearby is None:
            nearby = []
        leg = []
        for p in nearby:
            s= f"{p.index}".rjust(PADDING)
            leg.append(f"{s}  {p.name}")
        me = self.get_place_at_location(my_loc)
        if me:
            leg.append(f"{'{*}'.rjust(PADDING)}  {me.index} {me.name} (your current location)")
        else:
            leg.append(f"{'{.}'.rjust(PADDING)}  (your current location)")
        leg.append(f"{'.'.rjust(PADDING)}  Visited spaces")
        return "\n".join(leg)

    def render_all_visited(self, my_loc: tuple[int,int]):
        legend = self._render_legend(my_loc)
        me = self.get_place_at_location(my_loc)
        if me:
            fill = '*'
        else:
            fill = '.'
        return self.render(0, 0, self.cols, self.rows,
                           override_fn=generate_ship_function(my_loc, fill), visited_only=True) + legend

# number of spaces to move to get between 2 points assuming moving
# diagonal counts as one move
def distance_between_points(x1, y1, x2, y2):
    horz = abs(x2 - x1)
    vert = abs(y2 - y1)
    # min covers the diagonal movement, abs covers the remaining spaces
    return min(vert, horz) + abs(vert - horz)


# function to print a ship at a specific location
def generate_ship_function(location: tuple[int, int], fill):
    def inner_function(inner_loc):
        if location == inner_loc:
            return f"{{{fill}}}"
        else:
            return ""

    return inner_function


if __name__ == "__main__":
    world = Map(60, 25, 13)
    print(world)
    print(f"total places {world.num_places}")
    r = world.unused_get_nearby_places(world.places[0].location, 4, 5)
    for p in r:
        print(p.index)
    sub = world.render(24, 8, 44, 18, generate_ship_function((36, 10)))
    print(sub)
    sub = world.render(27, 16, 28, 17)
    print(sub)
