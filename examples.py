#!/usr/bin/env python3
"""
Example script showing how to use the new object-oriented Curve Fitter.

This demonstrates the improved API for various use cases.
"""

import os
import tempfile
import pandas as pd

# Set matplotlib backend for headless operation
os.environ['MPLBACKEND'] = 'Agg'

from src.curve_fitter import CurveFitter


def example_1_basic_usage():
    """Example 1: Basic curve fitting from coordinate string."""
    print("Example 1: Basic curve fitting from coordinates")
    print("-" * 50)
    
    # Create a curve fitter
    fitter = CurveFitter()
    
    # Fit curve from coordinate string
    coordinates = "(0, 10), (2, 5), (4, 15), (6, 8), (8, 12)"
    x_data, y_data = fitter.fit_from_coordinates(coordinates, show_plot=False)
    
    print(f"Input: {coordinates}")
    print(f"Generated {len(x_data)} interpolated points")
    print(f"X range: {x_data.min():.2f} to {x_data.max():.2f}")
    print(f"Y range: {y_data.min():.2f} to {y_data.max():.2f}")
    

def example_2_csv_data():
    """Example 2: Loading and fitting data from CSV."""
    print("\nExample 2: Loading data from CSV file")
    print("-" * 50)
    
    # Create a temporary CSV file with sample data
    sample_data = {
        'Time (hours)': [0, 6, 12, 18, 24],
        'Temperature (°C)': [15, 25, 30, 20, 16]
    }
    df = pd.DataFrame(sample_data)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        df.to_csv(f.name, index=False)
        temp_csv = f.name
    
    try:
        # Create curve fitter
        fitter = CurveFitter()
        
        # Load and fit data from CSV
        x_data, y_data, x_col, y_col = fitter.fit_from_csv(
            temp_csv, show_plot=False
        )
        
        print(f"Loaded data from CSV: {x_col} vs {y_col}")
        print(f"Original data points: {len(sample_data['Time (hours)'])}")
        print(f"Interpolated points: {len(x_data)}")
        
    finally:
        os.unlink(temp_csv)


def example_3_custom_styling():
    """Example 3: Custom plot styling and configuration."""
    print("\nExample 3: Custom styling and configuration")
    print("-" * 50)
    
    # Create curve fitter with custom plot configuration
    custom_config = {
        "curve_color": "green",
        "point_color": "red",
        "graph_title": "Custom Styled Sine Interpolation",
        "x_label": "Time (s)",
        "y_label": "Amplitude",
        "show_grid": True,
        "curve_line_width": 3,
        "figsize": (12, 6)
    }
    
    fitter = CurveFitter(plot_config=custom_config)
    
    # Sample data points
    points = [(0, 0), (1, 3), (2, -1), (3, 4), (4, 0)]
    
    x_data, y_data = fitter.fit_from_points(points, show_plot=False)
    
    print(f"Applied custom styling to plot")
    print(f"Plot title: {custom_config['graph_title']}")
    print(f"Curve color: {custom_config['curve_color']}")
    print(f"Point color: {custom_config['point_color']}")


def example_4_component_usage():
    """Example 4: Using individual components separately."""
    print("\nExample 4: Using individual components")
    print("-" * 50)
    
    from src.data_loader import DataLoader
    from src.interpolator import SineInterpolator
    from src.plotter import CurvePlotter
    
    # Use components individually
    data_loader = DataLoader()
    interpolator = SineInterpolator()
    plotter = CurvePlotter(config={"show_plot": False})
    
    # Parse some coordinates
    coord_string = "(0, 2), (1.5, 6), (3, 1), (4.5, 8), (6, 3)"
    points = data_loader.parse_coordinates(coord_string)
    print(f"DataLoader parsed {len(points)} points")
    
    # Perform interpolation
    x_data, y_data = interpolator.interpolate(points, points_per_segment=50)
    print(f"Interpolator generated {len(x_data)} points")
    
    # Create plot
    fig = plotter.plot_curve(x_data, y_data, points, show_plot=False)
    print(f"Plotter created figure with {len(fig.axes)} axes")


def example_5_high_precision():
    """Example 5: High precision interpolation settings."""
    print("\nExample 5: High precision interpolation")
    print("-" * 50)
    
    # Configure for high precision
    interpolator_config = {
        "newton_raphson_iterations": 100,
        "newton_raphson_tolerance": 1e-16
    }
    
    fitter = CurveFitter(interpolator_config=interpolator_config)
    
    # Test with challenging data (sharp changes)
    points = [(0, 0), (1, 10), (2, 0), (3, -10), (4, 0)]
    
    x_data, y_data = fitter.fit_from_points(points, show_plot=False)
    
    print(f"High precision interpolation of {len(points)} challenging points")
    print(f"Generated {len(x_data)} output points")
    print(f"Newton-Raphson iterations: {interpolator_config['newton_raphson_iterations']}")
    print(f"Tolerance: {interpolator_config['newton_raphson_tolerance']}")


if __name__ == "__main__":
    print("Curve Fitter Object-Oriented API Examples")
    print("=" * 60)
    
    example_1_basic_usage()
    example_2_csv_data()
    example_3_custom_styling()
    example_4_component_usage()
    example_5_high_precision()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("\nThe new object-oriented structure provides:")
    print("• Easy-to-use CurveFitter class for common tasks")
    print("• Individual components for specialized use cases")
    print("• Flexible configuration options")
    print("• Full backward compatibility with existing code")