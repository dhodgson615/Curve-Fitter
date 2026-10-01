from re import findall

from lib import COORDINATE_REGEX
from models import Point


def parse_coords(coordinate_string: str) -> list[Point]:
    """Convert text like "(1, 2), (3, 4)" into [(1.0, 2.0), (3.0, 4.0)]."""
    matches: list[tuple[str, str]] = findall(
        COORDINATE_REGEX, coordinate_string
    )

    return [(float(x), float(y)) for x, y in matches]
