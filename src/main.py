"""
Main module for the Curve Fitter application.

This module provides both the new object-oriented interface through the CurveFitter class
and maintains backward compatibility with the original procedural functions.
"""

from re import findall

import matplotlib.pyplot as plot
from numpy import array, cos, linspace, pi, sin
from pandas import read_csv

from src.config import (CSV_FILE, INTERPOLATION_CONFIG,
                        PLOT_CONFIG, SAMPLE_PLOT_CONFIG, SAMPLE_POINTS)
from src.curve_fitter import CurveFitter
from data.data_gen import generate

# Maintain backward compatibility with original regex constant
COORD_REGEX = r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)"


# Backward compatibility functions - these now delegate to the object-oriented classes
def parse_coords(s):
    """Parse coordinate string (backward compatibility function)."""
    from src.data_loader import DataLoader
    loader = DataLoader()
    return loader.parse_coordinates(s)


def f(x, x1, x2, y1, y2, n):
    """Sine interpolation function (backward compatibility function)."""
    from src.interpolator import SineInterpolator
    interpolator = SineInterpolator()
    return interpolator._sine_function(x, x1, x2, y1, y2, n)


def newton_raphson(x1, x2, y1, y2, iters=None, tol=None):
    """Newton-Raphson method (backward compatibility function)."""
    from src.interpolator import SineInterpolator
    interpolator = SineInterpolator(
        newton_raphson_iterations=iters,
        newton_raphson_tolerance=tol
    )
    return interpolator._newton_raphson(x1, x2, y1, y2)


def interpolate(pts, pts_per_seg=None):
    """Interpolate points (backward compatibility function)."""
    from src.interpolator import SineInterpolator
    interpolator = SineInterpolator()
    return interpolator.interpolate(pts, pts_per_seg)


def load_points_from_csv(filename, x_col=None, y_col=None):
    """Load points from CSV (backward compatibility function)."""
    from src.data_loader import DataLoader
    loader = DataLoader()
    points, x_col, y_col = loader.load_from_csv(filename, x_col, y_col)
    return points, x_col, y_col


def graph(points=None, config=None):
    """Create graph (backward compatibility function)."""
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


# Main execution remains the same for backward compatibility
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
