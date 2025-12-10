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

COORD_REGEX = r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)"


def parse_coords(s: str) -> list[tuple[float, float]]:
    return [(float(x), float(y)) for x, y in findall(COORD_REGEX, s)]


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
    pts: list[tuple[float, float]],
    pts_per_seg: int = int(INTERPOLATION_CONFIG["points_per_segment"]),
) -> tuple[list[float], list[float]]:
    """Interpolate a smooth curve through the given points."""
    return (
        [
            (x1 + (x2 - x1) / pts_per_seg * j)
            for (x1, y1), (x2, y2) in list(zip(sorted(pts), sorted(pts)[1:]))
            for j in range(pts_per_seg)
        ]
        + [float(pts[-1][0])],
        [
            f((x1 + (x2 - x1) / pts_per_seg * j), x1, x2, y1, y2, n)
            for (x1, y1), (x2, y2) in list(zip(sorted(pts), sorted(pts)[1:]))
            for n in [adjust_n(x1, x2, y1, y2)]
            for j in range(pts_per_seg)
        ]
        + [float(pts[-1][1])],
    )


def load_points_from_csv(
    filename: str,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
) -> tuple[list[tuple[float, float]], str, str]:
    """Load points from a CSV file"""
    df = read_csv(filename)
    x_col = x_col or df.columns[0]
    y_col = y_col or df.columns[1]

    points: list[tuple[float, float]] = [
        (float(x), float(y)) for x, y in zip(df[x_col], df[y_col])
    ]

    return points, x_col, y_col


def graph(
    pts: Optional[list[tuple[float, float]]] = None,
    config: Optional[dict[str, Any]] = None,
) -> Figure:
    """Create a graph from interpolated points"""
    cfg: dict[str, Any] = PLOT_CONFIG.copy()

    if config:
        cfg.update(config)

    pts = parse_coords(input(cfg["input_prompt"])) if pts is None else pts
    x, y = interpolate(pts)
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

    x_points, y_points = zip(*pts)

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
