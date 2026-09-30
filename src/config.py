"""Settings for the half-sine interpolation project"""

from pathlib import Path
from typing import Any, Union

from src.main import Point

# The folder that contains `src/` and `data/`. Found relative to this file so
# paths work no matter which directory you run Python from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Where `data/data_gen.py` writes its CSV of generated data.
CSV_FILE = str(PROJECT_ROOT / "data" / "data_points.csv")

# A small hand-picked data set, as (x, y) pairs.
SAMPLE_POINTS: list[Point] = [(0, 5), (2, 0), (4, 10), (6, 5), (8, 0)]

# Interpolation settings
INTERPOLATION_CONFIG: dict[str, Union[int, float]] = {
    # How many x-values to compute between each pair of neighboring points.
    # Higher = smoother curve, but slower.
    "points_per_segment": 250,
    # Newton-Raphson stops after this many steps...
    "newton_raphson_iterations": 30,
    # ...or as soon as the error is smaller than this.
    "newton_raphson_tolerance": 1e-12,
}

# Defaults used for every plot.
PLOT_CONFIG: dict[
    str, Union[str, tuple[float, float], float, bool, int, None]
] = {
    "plot_style": "dark_background",  # any matplotlib style name
    "figsize": (10.0, 6.0),  # (width, height) in inches
    "alpha": 1.0,  # opacity of curve and points: 0 = invisible, 1 = solid
    "show_grid": False,
    "show_plot": True,  # False = build the figure but don't open a window
    "curve_label": "Interpolated Curve",
    "curve_color": "blue",
    "curve_line_style": "-",
    "curve_line_width": 2,
    "point_label": "Original Points",
    "point_color": "red",
    "point_marker": "o",
    "graph_title": "Curve Interpolation Using Omega Function",
    "x_label": None,  # No label
    "y_label": None,
    "input_prompt": "Coordinates e.g. (1, 2), (3, 4): ",
}

# Settings shared by the two "sine interpolation" demos below.
_SINE_DEMO_SETTINGS: dict[str, Any] = {
    "plot_style": "dark_background",
    "figsize": (12, 8),
    "curve_label": "Sine Interpolation",
    "point_color": "yellow",
    "show_grid": True,
}

# Overrides for plotting points loaded from `CSV_FILE`.
CSV_PLOT_CONFIG: dict[str, Any] = {
    **_SINE_DEMO_SETTINGS,
    "point_label": "Data Points",
}

# Overrides for plotting `SAMPLE_POINTS`.
SAMPLE_PLOT_CONFIG: dict[str, Any] = {
    **_SINE_DEMO_SETTINGS,
    "point_label": "Sample Points",
    "graph_title": "Smooth Sine Interpolation Demo",
    "regenerate_points": True,
}
