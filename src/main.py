from __future__ import annotations

from math import cos, pi, sin
from os.path import abspath, dirname, join
from re import findall
from sys import path
from typing import Any, Optional

from matplotlib.figure import Figure
from matplotlib.pyplot import (figure, grid, legend, plot, scatter, show,
                               title, xlabel, ylabel)
from matplotlib.pyplot.style import use
from pandas import read_csv

# Add the project root to Python path when running directly
# TODO: Remove this hack
if __name__ == "__main__":
    path.insert(0, abspath(join(dirname(__file__), "..")))

try:
    from src.config import INTERPOLATION_CONFIG, PLOT_CONFIG

except ImportError:
    from config import INTERPOLATION_CONFIG, PLOT_CONFIG

COORDINATE_REGEX = r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)"


def parse_coords(coordinate_string: str) -> list[tuple[float, float]]:
    return [
        (float(x), float(y))
        for x, y in findall(COORDINATE_REGEX, coordinate_string)
    ]


def f(x: float, x1: float, x2: float, y1: float, y2: float, n: float) -> float:
    """Calculate interpolation value at x using sine function with adjustment n"""
    dx = x2 - x1
    val = (y1 + y2 + (y2 - y1) * sin(pi * (x - x2 - n) / dx)) / 2
    return float(val)


def adjust_n(
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    iterations: int = int(INTERPOLATION_CONFIG["newton_raphson_iterations"]),
    tolerance: float = float(INTERPOLATION_CONFIG["newton_raphson_tolerance"]),
) -> float:
    """Find adjustment value n using Newton-Raphson method"""
    assert x2 != x1, "Newton–Raphson derivative hit 0"
    n = 0.0
    dx = x2 - x1
    a = (y2 - y1) / 2

    for _ in range(iterations):
        t = pi * n / dx
        fn = a * sin(t) + (y1 + y2) / 2 - y1
        fp = a * cos(t) * pi / dx

        if abs(fn) < tolerance:
            break

        assert fp != 0, "Newton–Raphson derivative hit 0"
        n -= fn / fp

    return float(n)


def interpolate(
    points: list[tuple[float, float]],
    points_per_segment: int = DEFAULT_POINTS_PER_SEGMENT,
) -> tuple[
    list[float], list[float]
]:  # TODO: change this so that it returns a list[Point] instead of two lists
    """Compute a smooth curve through `points`.

    Returns two lists, `(x_values, y_values)`, ready to hand to a plotting
    function. Points are sorted by x first, so the input order doesn't matter.
    Each pair of neighboring points contributes `points_per_segment` samples,
    plus one final sample for the last point.
    """
    sorted_points: list[Point] = sorted(points)
    x_values: list[float] = []
    y_values: list[float] = []

    for (x1, y1), (x2, y2) in zip(sorted_points, sorted_points[1:]):
        n: float = find_phase_shift(x1, x2, y1, y2)  # once per segment
        step: float = (x2 - x1) / points_per_segment

        for j in range(points_per_segment):
            x = x1 + step * j
            x_values.append(x)
            y_values.append(half_sine(x, x1, x2, y1, y2, n))

    # The loop above stops just short of each segment's right end, so close the
    # curve off with the very last point.
    last_x, last_y = sorted_points[-1]
    x_values.append(float(last_x))
    y_values.append(float(last_y))

    return x_values, y_values


def load_points_from_csv(
    filename: str,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
) -> tuple[list[tuple[float, float]], str, str]:
    """Load points from a CSV file"""
    df = read_csv(filename)
    x_column = x_column or df.columns[0]
    y_column = y_column or df.columns[1]

    points: list[tuple[float, float]] = [
        (float(x), float(y)) for x, y in zip(df[x_column], df[y_column])
    ]

    return points, x_column, y_column


def graph(
    points: Optional[list[tuple[float, float]]] = None,
    config: Optional[dict[str, Any]] = None,
) -> Figure:
    """Create a graph from interpolated points"""
    cfg: dict[str, Any] = PLOT_CONFIG.copy()

    if config:
        cfg.update(config)

    points = (
        parse_coords(input(cfg["input_prompt"])) if points is None else points
    )

    x, y = interpolate(points)
    use(str(cfg["plot_style"]))
    fig = figure(figsize=cfg["figsize"])

    plot(
        x,
        y,
        label=str(cfg["curve_label"]),
        color=str(cfg["curve_color"]),
        linestyle=str(cfg["curve_line_style"]),
        linewidth=float(cfg["curve_line_width"]),
        alpha=float(cfg["alpha"]),
    )

    x_points, y_points = zip(*points)

    scatter(
        x_points,
        y_points,
        color=str(cfg["point_color"]),
        marker=str(cfg["point_marker"]),
        label=str(cfg["point_label"]),
        alpha=float(cfg["alpha"]),
    )

    title(cfg["graph_title"])

    if cfg["x_label"]:
        xlabel(cfg["x_label"])

    if cfg["y_label"]:
        ylabel(cfg["y_label"])

    legend()
    grid(cfg["show_grid"])

    if cfg["show_plot"]:
        show()

    return fig
