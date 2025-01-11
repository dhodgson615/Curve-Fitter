import numpy as np
import matplotlib.pyplot as plt

def parse_coordinates(input_str):
    """
    Manually parse a string of coordinates into a list of tuples.
    Input format: "(1, 2), (3, 4), (5, 6)"
    """
    try:
        # Remove whitespace and split into individual coordinate strings
        input_str = input_str.strip()
        if not input_str.startswith("(") or not input_str.endswith(")"):
            raise ValueError("Input must be in the format (x1, y1), (x2, y2), ...")
        
        # Split on "), (" to isolate each pair
        coordinate_strings = input_str.split("), (")
        coordinates = []
        
        for coord in coordinate_strings:
            # Clean up leading/trailing characters and split into x and y
            coord = coord.replace("(", "").replace(")", "")
            x, y = coord.split(",")
            coordinates.append((float(x.strip()), float(y.strip())))
        
        return coordinates
    except Exception as e:
        raise ValueError("Invalid input format. Ensure you use (x1, y1), (x2, y2), ...") from e


def omega_function(x, x1, x2, y1, y2, n30):
    """
    Compute the Omega function.
    """
    return (y2 - y1) / 2 * np.sin(np.pi * (x - x2 - n30) / (x2 - x1)) + (y1 + y2) / 2


def newton_raphson_n30(x1, x2, y1, y2, max_iterations=30, tolerance=1e-10):
    """
    Compute n30 using the Newton-Raphson method.
    """
    def f(n):
        return (y2 - y1) / 2 * np.sin(np.pi * n / (x2 - x1)) + (y1 + y2) / 2 - y1

    def f_prime(n):
        return (y2 - y1) / 2 * np.cos(np.pi * n / (x2 - x1)) * (np.pi / (x2 - x1))

    n = 0  # Initial guess
    for _ in range(max_iterations):
        fn = f(n)
        f_prime_n = f_prime(n)
        if abs(fn) < tolerance:
            break
        if f_prime_n == 0:
            raise ValueError("Derivative became zero during Newton-Raphson iterations.")
        n -= fn / f_prime_n
    return n


def interpolate_and_plot(points):
    """
    Interpolate the curve and plot the graph.
    """
    points = sorted(points, key=lambda p: p[0])  # Ensure points are sorted by x-coordinate
    x_values = np.linspace(points[0][0], points[-1][0], 1000)  # Fine-grained x-axis for plotting
    y_values = []

    # Loop through each segment and calculate corresponding Omega function
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        n30 = newton_raphson_n30(x1, x2, y1, y2)
        
        # Generate points for this segment
        segment_x = x_values[(x_values >= x1) & (x_values <= x2)]
        segment_y = omega_function(segment_x, x1, x2, y1, y2, n30)
        y_values.extend(segment_y)
    
    # Plot the curve
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
    """
    Main program to read input, process data, and generate the graph.
    """
    try:
        input_str = input("Provide a list of coordinates (e.g., (1, 2), (3, 4), (5, 6)): ")
        points = parse_coordinates(input_str)
        interpolate_and_plot(points)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
