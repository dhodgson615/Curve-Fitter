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

from graphing import graph

# Matches "(x, y)" pairs in text like "(1, 2), (3.5, -4)" and captures x and y.

# Defaults pulled from config.py so they can be changed in one place.


def main() -> None:
    """Ask for coordinates in the terminal, then plot the curve."""
    graph()


if __name__ == "__main__":
    main()


# Old names, kept so test/test_main.py still works. Once the tests use the
# new names (half_sine, find_phase_shift), delete these two lines.
