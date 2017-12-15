"""Utility functions for GiTils."""


def unravel_id(string_id):
    """Split a string into a traversable list."""
    return [s.lower() for s in string_id.split(".")]


def traverse(dictionary, directions):
    """Follow the path "directions" into the dictionary."""
    current_frame = dictionary
    for ind, loc in enumerate(directions):
        try:
            current_frame = current_frame[loc]
        except KeyError:
            ref = ".".join(directions[:ind])
            raise KeyError("{} doesn't exist in {}".format(loc, ref))

    return current_frame
