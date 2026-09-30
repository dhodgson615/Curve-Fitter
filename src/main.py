"""Half-sine interpolation: graph a smooth curve through a list of points.

Between each pair of neighboring points we draw half of a sine wave, shaped so
that the curve leaves and arrives flat (zero slope) and passes exactly through
both points. Chain those segments together and you get one smooth curve.

The README walks through the math. The variable names used here match it:
    (x1, y1) and (x2, y2)  the two points a segment connects
    n                      a sideways shift that lines the wave up with them

Run it from the project root (the folder that contains `src/`):

    python3 src/main.py

"""

from math import cos, pi, sin
from re import findall
from typing import Any, Optional, TypeAlias

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pandas import DataFrame, read_csv

from config import INTERPOLATION_CONFIG, PLOT_CONFIG

# A point is an (x, y) pair.
Point: TypeAlias = tuple[float, float]

# Matches "(x, y)" pairs in text like "(1, 2), (3.5, -4)" and captures x and y.
COORDINATE_REGEX: str = r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)"

# Defaults pulled from config.py so they can be changed in one place.
DEFAULT_POINTS_PER_SEGMENT: int = int(
    INTERPOLATION_CONFIG["points_per_segment"]
)

DEFAULT_NEWTON_ITERATIONS: int = int(
    INTERPOLATION_CONFIG["newton_raphson_iterations"]
)

DEFAULT_NEWTON_TOLERANCE: float = float(
    INTERPOLATION_CONFIG["newton_raphson_tolerance"]
)


def parse_coords(coordinate_string: str) -> list[Point]:
    """Convert text like "(1, 2), (3, 4)" into [(1.0, 2.0), (3.0, 4.0)]."""
    matches: list[tuple[str, str]] = findall(
        COORDINATE_REGEX, coordinate_string
    )

    return [(float(x), float(y)) for x, y in matches]


def half_sine(
    x: float, x1: float, x2: float, y1: float, y2: float, n: float
) -> float:
    """Height of the half-sine segment from (x1, y1) to (x2, y2) at `x`.

    This is the formula from the README:

        f(x) = ((y2 - y1) * sin(pi * (x - x2 - n) / (x2 - x1)) + y1 + y2) / 2

    `n` slides the wave sideways. Use `find_phase_shift` to get the `n`
    that makes the curve pass through both end points.
    """
    width: float = x2 - x1
    phase: float = pi * (x - x2 - n) / width
    return (y1 + y2 + (y2 - y1) * sin(phase)) / 2


def find_phase_shift(
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    iterations: int = DEFAULT_NEWTON_ITERATIONS,
    tolerance: float = DEFAULT_NEWTON_TOLERANCE,
) -> float:
    """Find the shift `n` that makes the segment start exactly at (x1, y1).

    We need half_sine(x1) == y1. With a = (y2 - y1) / 2, that works out to
    solving

        error(n) = a * (sin(pi * n / width) + 1) = 0

    Newton-Raphson does this by repeatedly nudging `n` by
    `error / slope` until the error is smaller than `tolerance`.
    """
    assert x1 != x2, "x1 and x2 must be different"
    width: float = x2 - x1
    amplitude: float = (y2 - y1) / 2
    n: float = 0.0  # starting guess

    for _ in range(iterations):
        angle: float = pi * n / width
        error: float = amplitude * sin(angle) + (y1 + y2) / 2 - y1
        slope: float = amplitude * cos(angle) * pi / width

        if abs(error) < tolerance:
            break

        assert slope != 0, "derivative hit zero in Newton-Raphson"
        n -= error / slope

    return float(n)


def interpolate(
    points: list[Point],
    points_per_segment: int = DEFAULT_POINTS_PER_SEGMENT,
) -> list[Point]:
    """Compute a smooth curve through `points`.

    Returns a list of `(x, y)` points ready to hand to a plotting function or
    processing pipeline. Points are sorted by x first, so the input order
    doesn't matter. Each pair of neighboring points contributes
    `points_per_segment` samples, plus one final sample for the last point.
    """
    assert len(points) >= 2, "At least 2 points are required for interpolation"
    sorted_points: list[Point] = sorted(points)
    curve_points: list[Point] = []

    x1: float
    y1: float
    x2: float
    y2: float

    for (x1, y1), (x2, y2) in zip(sorted_points, sorted_points[1:]):
        n: float = find_phase_shift(x1, x2, y1, y2)  # once per segment
        step: float = (x2 - x1) / points_per_segment

        for j in range(points_per_segment):
            x = x1 + step * j
            y = half_sine(x, x1, x2, y1, y2, n)
            curve_points.append((x, y))

    # The loop above stops just short of each segment's right end, so close the
    # curve off with the very last point.
    last_x, last_y = sorted_points[-1]
    curve_points.append((float(last_x), float(last_y)))

    return curve_points


def load_points_from_csv(
    filename: str,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
) -> tuple[list[Point], str, str]:
    """Read (x, y) points from a CSV file.

    By default, the first column is x and the second is y. Returns the points
    along with the column names used (handy for axis labels).
    """
    df: DataFrame = read_csv(filename)
    assert len(df.columns) >= 2, "CSV file must contain at least two columns"
    x_column = x_column or str(df.columns[0])
    y_column = y_column or str(df.columns[1])

    points: list[Point] = [
        (float(x), float(y)) for x, y in zip(df[x_column], df[y_column])
    ]

    return points, x_column, y_column


def graph(
    points: Optional[list[Point]] = None,
    config: Optional[dict[str, Any]] = None,
) -> Figure:
    """Plot the interpolated curve and the original points.

    `points`  the data to plot. If omitted, you're asked to type them in.
    `config`  settings that override the defaults in ``PLOT_CONFIG`` (see
              config.py for every option).
    """
    settings = {**PLOT_CONFIG, **(config or {})}

    if points is None:
        points = parse_coords(input(settings["input_prompt"]))

    curve_points: list[Point] = interpolate(points)

    curve_x = [point[0] for point in curve_points]
    curve_y = [point[1] for point in curve_points]

    point_xs = [point[0] for point in points]
    point_ys = [point[1] for point in points]

    plt.style.use(str(settings["plot_style"]))
    fig, ax = plt.subplots(figsize=settings["figsize"])

    ax.plot(
        curve_x,
        curve_y,
        label=str(settings["curve_label"]),
        color=str(settings["curve_color"]),
        linestyle=str(settings["curve_line_style"]),
        linewidth=float(settings["curve_line_width"]),
        alpha=float(settings["alpha"]),
    )

    ax.scatter(
        point_xs,
        point_ys,
        label=str(settings["point_label"]),
        color=str(settings["point_color"]),
        marker=str(settings["point_marker"]),
        alpha=float(settings["alpha"]),
    )

    ax.set_title(settings["graph_title"])

    if settings["x_label"]:
        ax.set_xlabel(settings["x_label"])

    if settings["y_label"]:
        ax.set_ylabel(settings["y_label"])

    ax.legend()
    ax.grid(settings["show_grid"])

    if settings["show_plot"]:
        plt.show()

    return fig


def main() -> None:
    """Ask for coordinates in the terminal, then plot the curve."""
    graph()


if __name__ == "__main__":
    main()


# Old names, kept so test/test_main.py still works. Once the tests use the
# new names (half_sine, find_phase_shift), delete these two lines.
f = half_sine
adjust_n = find_phase_shift
