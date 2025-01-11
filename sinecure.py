import numpy as np
import matplotlib.pyplot as plt

def parse_coordinates(input_str):
    try:
        input_str = input_str.strip()
        if not input_str.startswith("(") or not input_str.endswith(")"):
            raise ValueError("Input must be in the format (x1, y1), (x2, y2), ...")
        coordinate_strings = input_str.split("), (")
        coordinates = [parse_single_coordinate(coord) for coord in coordinate_strings]
        return coordinates
    except Exception as e:
        raise ValueError("Invalid input format. Ensure you use (x1, y1), (x2, y2), ...") from e

def parse_single_coordinate(coord):
    coord = coord.replace("(", "").replace(")", "")
    x, y = coord.split(",")
    return float(x.strip()), float(y.strip())

def omega_function(x, x1, x2, y1, y2, n30):
    return (y2 - y1) / 2 * np.sin(np.pi * (x - x2 - n30) / (x2 - x1)) + (y1 + y2) / 2

def newton_raphson_n30(x1, x2, y1, y2, max_iterations=30, tolerance=1e-12):
    def f(n):
        return (y2 - y1) / 2 * np.sin(np.pi * n / (x2 - x1)) + (y1 + y2) / 2 - y1

    def f_prime(n):
        return (y2 - y1) / 2 * np.cos(np.pi * n / (x2 - x1)) * (np.pi / (x2 - x1))

    n = 0  # Initial guess
    for _ in range(max_iterations):
        n = newton_raphson_iteration(n, f, f_prime, tolerance)
    return n

def newton_raphson_iteration(n, f, f_prime, tolerance):
    fn = f(n)
    f_prime_n = f_prime(n)
    if abs(fn) < tolerance:
        return n
    if f_prime_n == 0:
        raise ValueError("Derivative became zero during Newton-Raphson iterations.")
    return n - fn / f_prime_n

def interpolate(points):
    points = sorted(points, key=lambda p: p[0])
    x_values = np.linspace(points[0][0], points[-1][0], 1000)
    y_values = generate_interpolated_y_values(points, x_values)
    return x_values, y_values

def generate_interpolated_y_values(points, x_values):
    y_values = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        n30 = newton_raphson_n30(x1, x2, y1, y2)
        segment_x = x_values[(x_values >= x1) & (x_values <= x2)]
        segment_y = omega_function(segment_x, x1, x2, y1, y2, n30)
        y_values.extend(segment_y)
    return y_values

def plot(points, x_values, y_values):
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    plt.plot(x_values[:len(y_values)], y_values, label="Interpolated Curve")
    plt.scatter(*zip(*points), color='red', label="Original Points")
    plt.title("Curve Interpolation Using Omega Function")
    plt.xlabel("")
    plt.ylabel("")
    plt.legend()
    plt.grid(False)
    plt.show()

def main():
    try:
        input_str = input("Provide a list of coordinates (e.g., (1, 2), (3, 4), (5, 6)): ")
        points = parse_coordinates(input_str)
        x_values, y_values = interpolate(points)
        plot(points, x_values, y_values)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
