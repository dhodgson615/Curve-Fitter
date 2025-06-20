# Default plot styling configuration
PLOT_CONFIG = {
    "plot_style": "dark_background",
    "figsize": (10, 6),
    "curve_label": "Interpolated Curve",
    "curve_color": "blue",
    "curve_line_style": "-",
    "curve_line_width": 2,
    "point_color": "red",
    "point_marker": "o",
    "point_label": "Original Points",
    "graph_title": "Curve Interpolation Using Omega Function",
    "x_label": None,
    "y_label": None,
    "show_grid": False,
    "show_plot": True,
    "alpha": 1.0,
    "input_prompt": "Coordinates e.g. (1, 2), (3, 4): ",
}

# CSV configuration
CSV_FILE = "../data/data_points.csv"

# Default sample points if CSV is not found
SAMPLE_POINTS = [(0, 5), (2, 0), (4, 10), (6, 5), (8, 0)]

# Configuration for CSV data visualization
CSV_PLOT_CONFIG = {
    "plot_style": "dark_background",
    "figsize": (12, 8),
    "curve_label": "Sine Interpolation",
    "point_color": "yellow",
    "point_label": "Data Points",
    "show_grid": True,
}

# Configuration for sample data visualization
SAMPLE_PLOT_CONFIG = {
    "plot_style": "dark_background",
    "figsize": (12, 8),
    "curve_label": "Sine Interpolation",
    "point_color": "yellow",
    "point_label": "Sample Points",
    "graph_title": "Smooth Sine Interpolation Demo",
    "show_grid": True,
    "regenerate_points": True,
}

# Interpolation settings
INTERPOLATION_CONFIG = {
    "points_per_segment": 250,
    "newton_raphson_iterations": 30,
    "newton_raphson_tolerance": 1e-12,
}
