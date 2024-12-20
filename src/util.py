import base64
import pickle
import random


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


def as_int(v, def_val: int = -1):
    '''
    try converting v to int, returning default value if not possible or it's int value if so
    :param v:
    :return:
    '''
    try:
        i = int(v)
    except ValueError:
        return def_val
    return i


def clamp(value, minimum, maximum):
    """
    clamp a value to within a range
    """
    return max(minimum, min(value, maximum))


def choices_ex(rng, distribution, weights, exclude=None):
    '''
    Like random.choices but return a single item instead of an array. also excludes items in exclude
    :param rng: which rng to use
    :param dist:
    :param wght:
    :param exclude: this is a convenience. we have fixed lists of things that we pass for
        distribution and weights, this just lets us exclude items from them where exclude may be a
        variable.
    :return:
    '''
    dist = distribution.copy()
    wght = weights.copy()
    # Remove each value in exclude from dist and its corresponding element from wght
    if exclude is None:
        exclude = []
    for item in exclude:
        if item in dist:
            index_to_remove = dist.index(item)
            dist.pop(index_to_remove)
            wght.pop(index_to_remove)

    # Use random.choices to select a random element from dist with corresponding weights from wght
    selected_value = rng.choices(dist, weights=wght, k=1)[0]

    return selected_value


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

    def __init__(self, rng, in_list, partner_list=None):
        self.in_list = in_list
        self.partner_list = partner_list
        if not len(in_list):
            return
        if partner_list and len(partner_list) != len(in_list):
            raise ValueError("partner list size doesn't match")

        self.rng = rng
        # need ptrs so we dont shuffle the original list
        self.list_ptr = list(range(len(in_list)))
        self.index = len(in_list)

    def select(self):
        return self.select_with_partner()[0]

    def select_with_partner(self):
        if not len(self.in_list):
            return "", ""
        # If all words have been used, shuffle the list and reset the index
        if self.index == len(self.list_ptr):
            self.rng.shuffle(self.list_ptr)
            self.index = 0

        # Select the next word in the shuffled list
        selected_word = self.in_list[self.list_ptr[self.index]]
        if self.partner_list:
            partner_word = self.partner_list[self.list_ptr[self.index]]
        else:
            partner_word = ""
        self.index += 1
        return selected_word, partner_word



_valid_dirs = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']
_dir_names = ['North', 'North East', 'East', 'South East', 'South', 'South West', 'West', 'North West']
_dir_coords = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


def is_direction_valid(dir):
    return dir in _valid_dirs


def list_valid_directions():
    return ", ".join(_valid_dirs)

class Direction:
    def __init__(self, dir):
        if isinstance(dir, str):
            if dir not in _valid_dirs:
                raise Exception("invalid direction")
            self.dir = _valid_dirs.index(dir)
        elif isinstance(dir, int):
            if 0 <= dir <= 7:
                self.dir = dir
            else:
                raise Exception("Invalid direction")
        else:
            raise Exception("Invalid direction")



    def __str__(self):
        return _dir_names[self.dir]

    def __eq__(self, other):
        if isinstance(other, Direction):
            return self.dir == other.dir
        return False

    def to_coords(self):
        return _dir_coords[self.dir]

    def short(self):
        return _valid_dirs[self.dir]

    def add(self, points):
        """
        Add a number of points on the compass. Positive values move clockwise, negative values are ccw.
        Example dir is N, points is 1, new dir is NE. Points is -1, new dir is NW
        :param points: integer value
        :return:
        """
        new_dir = self.dir + points
        new_dir %= 8
        self.dir=new_dir

    def distance(self, other_dir):
        """
        returns the number of compass points to get from one point to another.
        eg nw and se would yield 4 as they are 4 points apart.
        :param other_dir:
        :return:
        """
        diff = abs(self.dir - other_dir.dir)
        return min(diff, 8 - diff)

def fancy_date(current_date):
    def ordinal_suffix(day):
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return suffix

    return f"{current_date.day}{ordinal_suffix(current_date.day)} of {current_date.strftime('%B')} {current_date.year}"


def fancy_time(current_time):
    # wrap around for convenience
    if current_time > 2:
        current_time=0

    if not current_time:
        return "morning"
    elif current_time == 1:
        return "afternoon"
    elif current_time == 2:
        return "evening"
    return "night"


def coord_as_str(coord: tuple[int, int]):
    return f"{coord[0]}E {coord[1]}S"


def direction_from_two_coords(a: tuple[int, int], b: tuple[int, int]):
    """
    Return the direction that b lies from a
    :param a:
    :param b:
    :return:
    """
    x = b[0] - a[0]
    y = b[1] - a[1]
    if not x and not y:
        return None
    # normalize: if one direction is 3x greater than other, eliminate other
    if abs(x) > abs(y) * 3:
        y = 0
    elif abs(y) > abs(x) * 3:
        x = 0

    if x:
        x = -1 if x < 0 else 1
    if y:
        y = -1 if y < 0 else 1

    diff = (x, y)
    ind = _dir_coords.index(diff)
    return Direction(_valid_dirs[ind])


def save_rng_state_to_string(rng):
    s = rng.getstate()
    pickled_data = pickle.dumps(s)
    encoded_data = base64.b64encode(pickled_data).decode('utf-8')
    return encoded_data


def load_rng_state_from_string(rng, state):
    pickled_data = base64.b64decode(state)
    s = pickle.loads(pickled_data)
    rng.setstate(s)


def deserialize_obj(obj, data):
    for s in obj._serialized_attrs:
        v = data[s]
        setattr(obj, s, v)


def serialize_obj(obj):
    r = {}
    for s in obj._serialized_attrs:
        r[s] = getattr(obj, s)
    return r

if __name__ == "__main__":
    print("")
