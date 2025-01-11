# Curve Interpolation Using Omega Function

This Python program generates a smooth interpolated curve through a given set of points using a custom `Omega` function. The interpolation is performed segment-by-segment, ensuring the curve transitions smoothly while aligning with the provided data points.

## Features
- Interpolates between points using a sine-based `Omega` function.
- Calculates alignment offset (`n_30`) using the Newton-Raphson method.
- Supports an arbitrary number of points with ascending x-values.
- Visualizes the resulting curve using Matplotlib with a dark mode theme.

## Requirements
- Python 3.7 or higher
- Libraries: `numpy`, `matplotlib`

Install dependencies using:
`pip install numpy matplotlib`

## Usage

1. **Run the Program**: `python main.py`
2. **Input Points**: Provide a list of coordinates in the format:
`(x1, y1), (x2, y2), (x3, y3), ...`
Example:
`(-10, -5), (-8, -10), (-6, -3), (-4, 0), (-2, 2), (0, -1), (2, 6)`
3. **Output**: A graph is generated showing:
   - The interpolated curve.
   - Original points as red dots.

## Key Functions
- `parse_coordinates`: Parses user input into valid `(x, y)` tuples.
- `omega_function`: Implements the sine-based interpolation formula.
- `newton_raphson_n30`: Calculates the `n_30` offset using the Newton-Raphson method.
- `interpolate_and_plot`: Handles the curve interpolation and visualization.

## Dark Mode Theme
The graph uses a dark theme for better visibility. To change this, update the `plt.style.use()` line in the script.

## Contribution
Fork the repository and create pull requests to suggest improvements or fixes.

## License
This project is licensed under the MIT License.
