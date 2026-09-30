from typing import Any, Optional, Union

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from src.config import PLOT_CONFIG
from src.main import interpolate
from src.types import Point
from src.utils import parse_coords


def graph(
    points: Optional[list[Point]] = None,
    config: Optional[dict[str, Any]] = None,
) -> Figure:
    """Plot the interpolated curve and the original points.

    `points`  the data to plot. If omitted, you're asked to type them in.
    `config`  settings that override the defaults in ``PLOT_CONFIG`` (see
              config.py for every option).
    """
    settings: dict[
        str,
        Union[str, Point, float, bool, int, None],
    ] = {
        **PLOT_CONFIG,
        **(config or {}),
    }  # TODO: refactor this so that the individual labels are sourced from the
    #          appropriate configuration fields

    if points is None:
        points = parse_coords(input(settings["input_prompt"]))

    curve_points: list[Point] = interpolate(points)

    curve_xs: list[float] = [point[0] for point in curve_points]
    curve_ys: list[float] = [point[1] for point in curve_points]
    point_xs: list[float] = [point[0] for point in points]
    point_ys: list[float] = [point[1] for point in points]

    plt.style.use(str(settings["plot_style"]))
    figure, axes = plt.subplots(figsize=settings["figsize"])

    axes.plot(
        curve_xs,
        curve_ys,
        label=str(settings["curve_label"]),
        color=str(settings["curve_color"]),
        linestyle=str(settings["curve_line_style"]),
        linewidth=float(settings["curve_line_width"]),
        alpha=float(settings["alpha"]),
    )

    axes.scatter(
        point_xs,
        point_ys,
        label=str(settings["point_label"]),
        color=str(settings["point_color"]),
        marker=str(settings["point_marker"]),
        alpha=float(settings["alpha"]),
    )

    axes.set_title(settings["graph_title"])

    if settings["x_label"]:
        axes.set_xlabel(settings["x_label"])

    if settings["y_label"]:
        axes.set_ylabel(settings["y_label"])

    axes.legend()
    axes.grid(settings["show_grid"])

    if settings["show_plot"]:
        plt.show()

    return figure
