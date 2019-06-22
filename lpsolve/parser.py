


def parse_file(filename):
    """Parse a LP file with a given filename, returning an
    intermediate representation that is of use for further solving."""

    with open(filename) as fin:
        return parse_string(fin.read())

def parse_string(string):
    """Parse an LP-format string, returning an intermediate representation
    that is of use for further solver stages"""

    print(f" -> {string}")

    return None





