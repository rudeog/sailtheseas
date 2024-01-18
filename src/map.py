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
        self.populated = False  # meaning it has an island
        self.visited = False
        self.index = -1
        self.name: str = ""
        self.port = None

    # set the location as being populated
    def set_place(self, idx):
        self.populated = True
        self.index = idx

    # visited_only: will only dump it if its been visited
    def dump(self, padding, visited_only, my_loc):
        if self.populated: # has island
            if (visited_only and self.visited) or not visited_only:
                if my_loc:
                    v = f"{{{self.index}}}"
                else:
                    v = f"{self.index}"
                vv = v.center(padding)
                return vv
        if self.visited:
            if my_loc:
                return "{.}".center(padding)
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

    def get_all_nearby_places(self, location: tuple[int, int], count_only: bool = False,
                              dist: int = LOCAL_VIEW_SIZE, exclude_center: bool = False):
        '''
        given a center point returns a list of locations in the area centered at that point.
        :param exclude_center: if true will exclude the specified location if it is a populated square
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
                if self.map[yy][xx].populated:
                    if not(exclude_center and (yy == y and xx == x)):
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
            count = self.get_all_nearby_places((x, y), True, 1, True)
            if not count:
                return (x, y)
            t = t - 1
        raise Exception(f"failed to get validated location after {self.rows * self.cols} tries!")

    def get_place_at_location(self, location: tuple[int, int]):
        """
        Get a place that is within a location. return None if there isnt any in that square
        :return:
        """
        for p in self.places:
            if p.location == location:
                return p
        return None

    def __str__(self):
        return self.render(0, 0, self.cols, self.rows)

    def render(self, xstart, ystart, xend, yend, my_loc, visited_only=False):
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
        trims = [0] * len(parts)
        y = ystart
        for row in self.map[ystart:yend]:
            if INCLUDE_XY_RULER:
                rh = str(y).rjust(padding)
            else:
                rh = ""
            parts.append(rh + "|")
            trims.append(0)
            x = xstart
            for item in row[xstart:xend]:
                to_add = item.dump(padding, visited_only, my_loc==(x,y))
                trims.append(len(to_add))
                parts.append(f"{to_add}")
                x += 1
            parts.append("|\n")
            trims.append(0)
            y = y + 1
        parts.append(hdr)
        trims.append(0)

        ind = 0
        result = ""
        # parts within the grid that have size >3 need to have surrounding parts shrunk.
        # if its 4 we shrink the one after it, if its 5 we shrink both before and after
        pi=0
        for t in trims:
            if t > 3:
                parts[pi+1] = parts[pi+1][1:]
            if t ==5:
                parts[pi-1] = parts[pi-1][:-1]
            pi += 1
        for p in parts:
            result = result + p
            ind += 1

        return result

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
        legend = self._render_legend(nearby)
        ret_map = self.render(xstart,ystart,xend,yend,my_loc)
        return ret_map + legend

    def _render_legend(self, nearby=None):
        if nearby is None:
            nearby = []
        leg = []
        for p in nearby:
            s= f"{p.index}".rjust(PADDING)
            leg.append(f"{s}  {p.name}")
        leg.append(f"{'{ }'.rjust(PADDING)}  (your current location)")
        leg.append(f"{'.'.rjust(PADDING)}  Visited spaces")
        return "\n".join(leg)


    def render_all_visited(self, my_loc: tuple[int,int]):
        # this is to print the full world map with places visited being rendered.
        legend = self._render_legend()
        return self.render(0, 0, self.cols, self.rows,
                            my_loc, visited_only=True) + legend


if __name__ == "__main__":
    world = Map(60, 25, 13)
    print(world)
    print(f"total places {world.num_places}")
    sub = world.render(27, 16, 28, 17)
    print(sub)
