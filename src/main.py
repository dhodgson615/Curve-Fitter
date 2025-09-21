import os
import re
import sys
import typing

import matplotlib.pyplot
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.figure import Figure

# Add the project root to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )

try:
    from src import config as config_module

except ImportError:
    import config as config_module  # type: ignore

COORD_REGEX = r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)"


def parse_coords(s: str) -> list[tuple[float, float]]:
    return [(float(x), float(y)) for x, y in re.findall(COORD_REGEX, s)]


def f(
    x: typing.Union[float, npt.NDArray[np.float64]],
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    n: float,
) -> npt.NDArray[np.float64]:
    """Calculate interpolation values using sine function with
    adjustment n
    """
    if isinstance(x, float):
        x_array = np.array([x], dtype=np.float64)

    else:
        x_array = x

    result = (y2 - y1) / 2 * np.sin(np.pi * (x_array - x2 - n) / (x2 - x1)) + (
        y1 + y2
    ) / 2

    return np.asarray(result, dtype=np.float64)


def newton_raphson(
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    iters: typing.Optional[int] = None,
    tol: typing.Optional[float] = None,
) -> float:
    """Find adjustment value n using Newton-Raphson method"""
    iterations: int = (
        iters
        if iters is not None
        else int(
            config_module.INTERPOLATION_CONFIG["newton_raphson_iterations"]
        )
    )

    tolerance: float = (
        tol
        if tol is not None
        else float(
            config_module.INTERPOLATION_CONFIG["newton_raphson_tolerance"]
        )
    )

    # Divide by zero check
    if x2 == x1:
        raise ValueError("Newton–Raphson derivative hit zero")

    n = 0.0
    for _ in range(iterations):
        fn = (y2 - y1) / 2 * np.sin(np.pi * n / (x2 - x1)) + (y1 + y2) / 2 - y1
        fp = (y2 - y1) / 2 * np.cos(np.pi * n / (x2 - x1)) * np.pi / (x2 - x1)

        if abs(fn) < tolerance:
            break
            
        if fp == 0:
            raise ValueError("Newton–Raphson derivative hit zero")

        n -= fn / fp

    return n


def interpolate(pts, pts_per_seg=None):
    pts_per_seg = pts_per_seg or INTERPOLATION_CONFIG["points_per_segment"]
    pts = sorted(pts)
    xs_out, ys_out = [], []

    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        seg_x = linspace(x1, x2, pts_per_seg, endpoint=False)
        seg_y = f(seg_x, x1, x2, y1, y2, newton_raphson(x1, x2, y1, y2))
        xs_out.extend(seg_x)
        ys_out.extend(seg_y)

    xs_out.append(pts[-1][0])
    ys_out.append(pts[-1][1])

    return array(xs_out), array(ys_out)


def load_points_from_csv(filename, x_col=None, y_col=None):
    df = read_csv(filename)
    x_col = x_col or df.columns[0]
    y_col = y_col or df.columns[1]
    return list(zip(df[x_col], df[y_col])), x_col, y_col


def graph(points=None, config=None):
    # Use default config if none provided
    cfg = PLOT_CONFIG.copy()
    if config:
        cfg.update(config)

    # Get points if not provided
    if points is None:
        points = parse_coords(input(cfg["input_prompt"]))

    # Generate interpolation
    x, y = interpolate(points)

    # Set up plot
    plot.style.use(cfg["plot_style"])
    fig = plot.figure(figsize=cfg["figsize"])

    # Plot curve and points
    plot.plot(
        x,
        y,
        label=cfg["curve_label"],
        color=cfg["curve_color"],
        linestyle=cfg["curve_line_style"],
        linewidth=cfg["curve_line_width"],
        alpha=cfg["alpha"],
    )

    plot.scatter(
        *zip(*points),
        color=cfg["point_color"],
        marker=cfg["point_marker"],
        label=cfg["point_label"],
        alpha=cfg["alpha"],
    )

    # Add labels and customize
    plot.title(cfg["graph_title"])
    if cfg["x_label"]:
        plot.xlabel(cfg["x_label"])
    if cfg["y_label"]:
        plot.ylabel(cfg["y_label"])

    plot.legend()
    plot.grid(cfg["show_grid"])

    if cfg["show_plot"]:
        plot.show()

    return fig


if __name__ == "__main__":
    if SAMPLE_PLOT_CONFIG.get("regenerate_points", True):
        generate()

    try:
        data_points, x_column, y_column = load_points_from_csv(CSV_FILE)
        graph(points=data_points)

    except FileNotFoundError:
        print(f"CSV file '{CSV_FILE}' not found. Using sample points instead.")
        graph(points=SAMPLE_POINTS, config=SAMPLE_PLOT_CONFIG)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
