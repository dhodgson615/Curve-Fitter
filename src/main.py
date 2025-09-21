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


# Fixed interpolate function handling None types and array types
def interpolate(
    pts: list[tuple[float, float]], pts_per_seg: typing.Optional[int] = None
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Interpolate a smooth curve through the given points"""
    points_per_segment: int = (
        pts_per_seg
        if pts_per_seg is not None
        else int(config_module.INTERPOLATION_CONFIG["points_per_segment"])
    )

    pts = sorted(pts)
    xs_out: list[float] = []
    ys_out: list[float] = []

    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]

        seg_x = np.linspace(
            x1, x2, points_per_segment, endpoint=False, dtype=np.float64
        )
        
        seg_y = f(seg_x, x1, x2, y1, y2, newton_raphson(x1, x2, y1, y2))
        xs_out.extend(seg_x)
        ys_out.extend(seg_y)

    xs_out.append(pts[-1][0])
    ys_out.append(pts[-1][1])

    return np.array(xs_out, dtype=np.float64), np.array(
        ys_out, dtype=np.float64
    )


def load_points_from_csv(
    filename: str,
    x_col: typing.Optional[str] = None,
    y_col: typing.Optional[str] = None,
) -> tuple[list[tuple[float, float]], str, str]:
    """Load points from a CSV file"""
    df = pd.read_csv(filename)
    x_col = x_col or df.columns[0]
    y_col = y_col or df.columns[1]
    
    return list(zip(df[x_col], df[y_col])), x_col, y_col


def graph(
    points: typing.Optional[list[tuple[float, float]]] = None,
    config: typing.Optional[typing.Dict[str, typing.Any]] = None,
) -> Figure:
    """Create a graph from interpolated points"""
    # Use default config if none provided
    cfg: typing.Dict[str, typing.Any] = config_module.PLOT_CONFIG.copy()

    if config:
        cfg.update(config)

    # Get points if not provided
    if points is None:
        points = parse_coords(input(cfg["input_prompt"]))

    # Generate interpolation
    x, y = interpolate(points)

    # Set up plot
    matplotlib.pyplot.style.use(str(cfg["plot_style"]))

    fig = matplotlib.pyplot.figure(
        figsize=typing.cast(tuple[float, float], cfg["figsize"])
    )

    # Plot curve and points
    matplotlib.pyplot.plot(
        x,
        y,
        label=str(cfg["curve_label"]),
        color=str(cfg["curve_color"]),
        linestyle=str(cfg["curve_line_style"]),
        linewidth=float(cfg["curve_line_width"]),
        alpha=float(cfg["alpha"]),
    )

    x_points, y_points = zip(*points)
    
    matplotlib.pyplot.scatter(
        x_points,
        y_points,
        color=str(cfg["point_color"]),
        marker=str(cfg["point_marker"]),
        label=str(cfg["point_label"]),
        alpha=float(cfg["alpha"]),
    )

    # Add labels and customize
    matplotlib.pyplot.title(str(cfg["graph_title"]))

    if cfg["x_label"]:
        matplotlib.pyplot.xlabel(str(cfg["x_label"]))

    if cfg["y_label"]:
        matplotlib.pyplot.ylabel(str(cfg["y_label"]))

    matplotlib.pyplot.legend()
    matplotlib.pyplot.grid(bool(cfg["show_grid"]))

    if cfg["show_plot"]:
        matplotlib.pyplot.show()

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
