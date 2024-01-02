

def clamp(value, minimum, maximum):
    """
    clamp a value to within a range
    """
    return max(minimum, min(value, maximum))


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