from os.path import abspath, dirname, join
from re import findall
from sys import path
from typing import Any, Optional, Union, cast

from matplotlib.figure import Figure
from matplotlib.pyplot import (figure, grid, legend, plot, scatter, show,
                               title, xlabel, ylabel)
from matplotlib.pyplot.style import use
from numpy import array, asarray, cos, float64, linspace, pi, sin
from numpy.typing import NDArray
from pandas import read_csv

# Add the project root to Python path when running directly
# TODO: Remove this hack
if __name__ == "__main__":
    path.insert(0, abspath(join(dirname(__file__), "..")))

try:
    from src import config as config_module

except ImportError:
    from config import INTERPOLATION_CONFIG, PLOT_CONFIG

COORD_REGEX = r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)"


def parse_coords(s: str) -> list[tuple[float, float]]:
    return [(float(x), float(y)) for x, y in findall(COORD_REGEX, s)]


def f(
    x: Union[float, NDArray[float64]],
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    n: float,
) -> NDArray[float64]:
    """Calculate interpolation values using sine function with
    adjustment n
    """
    x_array = array([x], dtype=float64) if isinstance(x, float) else x

    result = (y2 - y1) / 2 * sin(pi * (x_array - x2 - n) / (x2 - x1)) + (
        y1 + y2
    ) / 2

    return asarray(result, dtype=float64)


def newton_raphson(
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    iters: Optional[int] = None,
    tol: Optional[float] = None,
) -> float:
    """Find adjustment value n using Newton-Raphson method"""
    iterations: int = (
        iters
        if iters is not None
        else int(INTERPOLATION_CONFIG["newton_raphson_iterations"])
    )

    tolerance: float = (
        tol
        if tol is not None
        else float(INTERPOLATION_CONFIG["newton_raphson_tolerance"])
    )

    if x2 == x1:
        raise ValueError("Newton–Raphson derivative hit zero")

    n = 0.0

    for _ in range(iterations):
        fn = (y2 - y1) / 2 * sin(pi * n / (x2 - x1)) + (y1 + y2) / 2 - y1
        fp = (y2 - y1) / 2 * cos(pi * n / (x2 - x1)) * pi / (x2 - x1)

        if abs(fn) < tolerance:
            break

        if fp == 0:
            raise ValueError("Newton–Raphson derivative hit zero")

        n -= fn / fp

    return n


def interpolate(
    pts: list[tuple[float, float]], pts_per_seg: Optional[int] = None
) -> tuple[NDArray[float64], NDArray[float64]]:
    """Interpolate a smooth curve through the given points"""
    points_per_segment: int = (
        pts_per_seg
        if pts_per_seg is not None
        else int(INTERPOLATION_CONFIG["points_per_segment"])
    )

    pts = sorted(pts)
    xs_out: list[float] = []
    ys_out: list[float] = []

    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]

        seg_x = linspace(
            x1, x2, points_per_segment, endpoint=False, dtype=float64
        )

        seg_y = f(seg_x, x1, x2, y1, y2, newton_raphson(x1, x2, y1, y2))
        xs_out.extend(seg_x)
        ys_out.extend(seg_y)

    xs_out.append(pts[-1][0])
    ys_out.append(pts[-1][1])
    return array(xs_out, dtype=float64), array(ys_out, dtype=float64)


def load_points_from_csv(
    filename: str,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
) -> tuple[list[tuple[float, float]], str, str]:
    """Load points from a CSV file"""
    df = read_csv(filename)
    x_col, y_col = x_col or df.columns[0], y_col or df.columns[1]
    return list(zip(df[x_col], df[y_col])), x_col, y_col


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
    fig = figure(figsize=cast(tuple[float, float], cfg["figsize"]))

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

    title(str(cfg["graph_title"]))

    if cfg["x_label"]:
        xlabel(str(cfg["x_label"]))

    if cfg["y_label"]:
        ylabel(str(cfg["y_label"]))

    legend()
    grid(bool(cfg["show_grid"]))

    if cfg["show_plot"]:
        show()

    return fig
