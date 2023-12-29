

def clamp(value, minimum, maximum):
    """
    clamp a value to within a range
    """
    return max(minimum, min(value, maximum))


def to_proper_case(input_string):
    if not input_string:
        return input_string
    return input_string[0].upper() + input_string[1:].lower()