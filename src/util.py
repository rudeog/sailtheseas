
def custom_hash(string):
    """
    Stable hash function so we can get same hash between runs
    :param string:
    :return:
    """
    prime = 31
    result = 0

    for char in string:
        result = (result * prime + ord(char)) & 0xFFFFFFFF

    return result

def clamp(value, minimum, maximum):
    """
    clamp a value to within a range
    """
    return max(minimum, min(value, maximum))


def add_pair(a: tuple[int, int], b: tuple[int, int]):
    return (a[0] + b[0], a[1] + b[1])


def to_proper_case(input_string):
    if not input_string:
        return input_string
    return input_string[0].upper() + input_string[1:].lower()


class ListSelector:
    """
    Given a list will randomly select an item from the list without
    reusing items until all items are used then it should reshuffle
    the list
    """

    def __init__(self, rng, list):
        self.rng = rng
        self.list = list
        self.index = len(list)

    def select(self):
        # If all words have been used, shuffle the list and reset the index
        if self.index == len(self.list):
            self.rng.shuffle(self.list)
            self.index = 0

        # Select the next word in the shuffled list
        selected_word = self.list[self.index]
        self.index += 1
        return selected_word


_valid_dirs = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']
_dir_names = ['North', 'North East', 'East', 'South East', 'South', 'South West', 'West', 'North West']
_dir_coords = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


def is_direction_valid(dir):
    return dir in _valid_dirs


def list_valid_directions():
    return ", ".join(_valid_dirs)


class Direction:
    def __init__(self, dir):
        if dir not in _valid_dirs:
            raise Exception("invalid direction")
        self.dir = _valid_dirs.index(dir)

    def __str__(self):
        return _dir_names[self.dir]
    def __eq__(self, other):
        if isinstance(other, Direction):
            return self.dir == other.dir
        return False
    def to_coords(self):
        return _dir_coords[self.dir]


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
