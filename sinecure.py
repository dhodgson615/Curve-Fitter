from typing import Callable

import matplotlib.pyplot as plt
import numpy as np


def parse_coordinates(input_str: str) -> list[tuple[float, float]]:
    """Parse a string of coordinates in the format (x1, y1), (x2, y2),
    (x3, y3), ... and returns a list of tuples (x, y)."""
    try:
        input_str = input_str.strip()
        if not input_str.startswith("(") or not input_str.endswith(")"):
            raise ValueError(
                "Input must be in the format (x1, y1), (x2, y2), ..."
            )
        coordinate_strings: list[str] = input_str.split("), (")
        coordinates: list[tuple[float, float]] = [
            parse_single_coordinate(coord) for coord in coordinate_strings
        ]
        return coordinates
    except Exception as e:
        raise ValueError(
            "Invalid input format. Ensure you use (x1, y1), (x2, y2), ..."
        ) from e


def parse_single_coordinate(coord: str) -> tuple[float, float]:
    """Parse a single coordinate string in the format (x, y) and return
    a tuple (x, y)."""
    coord = coord.replace("(", "").replace(")", "")
    x_str, y_str = coord.split(",")
    return float(x_str.strip()), float(y_str.strip())


def omega_function(
    x: np.ndarray, x1: float, x2: float, y1: float, y2: float, n30: float
) -> np.ndarray:
    """Calculate the omega function for a given range of x values."""
    return (y2 - y1) / 2 * np.sin(np.pi * (x - x2 - n30) / (x2 - x1)) + (
        y1 + y2
    ) / 2


def newton_raphson_n30(
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    max_iterations: int = 30,
    tolerance: float = 1e-12,
) -> float:
    """Find the value of n30 using the Newton-Raphson method."""
    def f(n: float) -> float:
        """Function to find the root of."""
        return (
            (y2 - y1) / 2 * np.sin(np.pi * n / (x2 - x1)) + (y1 + y2) / 2 - y1
        )

    def f_prime(n: float) -> float:
        """Derivative of the function."""
        return (
            (y2 - y1) / 2 * np.cos(np.pi * n / (x2 - x1)) * (np.pi / (x2 - x1))
        )

    n: float = 0.0  # Initial guess
    for _ in range(max_iterations):
        n = newton_raphson_iteration(n, f, f_prime, tolerance)
    return n


def newton_raphson_iteration(
    n: float,
    f: Callable[[float], float],
    f_prime: Callable[[float], float],
    tolerance: float,
) -> float:
    """Perform a single iteration of the Newton-Raphson method."""
    fn: float = f(n)
    f_prime_n: float = f_prime(n)
    if abs(fn) < tolerance:
        return n
    if f_prime_n == 0:
        raise ValueError(
            "Derivative became zero during Newton-Raphson iterations."
        )
    return n - fn / f_prime_n


def interpolate(
    points: list[tuple[float, float]],
) -> tuple[np.ndarray, list[float]]:
    """Interpolate the given points using the omega function."""
    points = sorted(points, key=lambda p: p[0])
    x_values: np.ndarray = np.linspace(points[0][0], points[-1][0], 1000)
    y_values: list[float] = generate_interpolated_y_values(points, x_values)
    return x_values, y_values


def generate_interpolated_y_values(
    points: list[tuple[float, float]], x_values: np.ndarray
) -> list[float]:
    """Generate interpolated y values for the given x values using the
    omega function."""
    y_values: list[float] = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        n30: float = newton_raphson_n30(x1, x2, y1, y2)
        segment_x: np.ndarray = x_values[(x_values >= x1) & (x_values <= x2)]
        segment_y: np.ndarray = omega_function(segment_x, x1, x2, y1, y2, n30)
        y_values.extend(segment_y.tolist())
    return y_values


def plot(
    points: list[tuple[float, float]],
    x_values: np.ndarray,
    y_values: list[float],
) -> None:
    """Plot the original points and the interpolated curve."""
    plt.style.use("dark_background")
    plt.figure(figsize=(10, 6))
    plt.plot(x_values[: len(y_values)], y_values, label="Interpolated Curve")
    plt.scatter(*zip(*points), color="red", label="Original Points")
    plt.title("Curve Interpolation Using Omega Function")
    plt.xlabel("")
    plt.ylabel("")
    plt.legend()
    plt.grid(False)
    plt.show()


def main() -> None:
    """Main function to run the interpolation and plotting."""
    try:
        input_str: str = input(
            "Provide a list of coordinates (e.g., (1, 2), (3, 4), (5, 6)): "
        )
        points: list[tuple[float, float]] = parse_coordinates(input_str)
        x_values: np.ndarray
        y_values: list[float]
        x_values, y_values = interpolate(points)
        plot(points, x_values, y_values)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
