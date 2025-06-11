from re import findall

from matplotlib.pyplot import figure, grid, legend, plot, scatter, show, style, title
from numpy import array, cos, linspace, pi, sin

COORD_REGEX = r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)"


def parse_coords(s):
    return [tuple(map(float, m)) for m in findall(COORD_REGEX, s)]


def f(x, x1, x2, y1, y2, n):
    return (y2 - y1) / 2 * sin(pi * (x - x2 - n) / (x2 - x1)) + (y1 + y2) / 2


def newton_raphson(x1, x2, y1, y2, iters=30, tol=1e-12):
    n = 0.0

    for _ in range(iters):
        fn = (y2 - y1) / 2 * sin(pi * n / (x2 - x1)) + (y1 + y2) / 2 - y1
        fp = (y2 - y1) / 2 * cos(pi * n / (x2 - x1)) * pi / (x2 - x1)

        if abs(fn) < tol:
            break
        if fp == 0:
            raise ValueError("Newton–Raphson derivative hit zero")

        n -= fn / fp

    return n


def interpolate(pts, pts_per_seg=250):
    pts = sorted(pts)
    xs_out, ys_out = [], []

    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        seg_x = linspace(x1, x2, pts_per_seg, endpoint=False)
        seg_y = f(seg_x, x1, x2, y1, y2, newton_raphson(x1, x2, y1, y2))
        xs_out.extend(seg_x)
        ys_out.extend(seg_y)

    xs_out.append(pts[-1][0])
    ys_out.append(pts[-1][1])

    return array(xs_out), array(ys_out)


def main():
    pts = parse_coords(input("Coordinates e.g. (1, 2), (3, 4): "))
    x, y = interpolate(pts)
    style.use("dark_background")
    figure(figsize=(10, 6))
    plot(x, y, label="Interpolated Curve")
    scatter(*zip(*pts), color="red", label="Original Points")
    title("Curve Interpolation Using Omega Function")
    legend()
    grid(False)
    show()


if __name__ == "__main__":
    main()
