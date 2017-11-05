def unravel_id(string_id):
    return [s.lower() for s in string_id.split(".")]


def traverse(dictionary, directions):
    current_frame = dictionary
    for ind, loc in enumerate(directions):
        try:
            current_frame = current_frame[loc]
        except KeyError:
            ref = ".".join(directions[:ind])
            raise KeyError("{} doesn't exist in {}".format(loc, ref))

    return current_frame
