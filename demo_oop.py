#!/usr/bin/env python3
"""
Demonstration script showing the new object-oriented structure and its extensibility.

This script demonstrates how the refactored code is more extensible and easier to work with.
"""

import os
import matplotlib.pyplot as plt

# Set matplotlib backend for demonstration
os.environ['MPLBACKEND'] = 'Agg'

from src.curve_fitter import CurveFitter
from src.interpolator import SineInterpolator
from src.data_loader import DataLoader
from src.plotter import CurvePlotter


def demonstrate_basic_usage():
    """Demonstrate basic usage of the new OOP interface."""
    print("=== Basic OOP Usage ===")
    
    # Create a curve fitter
    fitter = CurveFitter()
    
    # Fit curve from coordinate string
    coord_string = "(0, 5), (2, 0), (4, 10), (6, 5), (8, 0)"
    x_data, y_data = fitter.fit_from_points(
        fitter.data_loader.parse_coordinates(coord_string), 
        show_plot=False
    )
    
    print(f"Generated {len(x_data)} interpolated points from coordinate string")
    print("Points pass through:", fitter.get_last_points())


def demonstrate_customization():
    """Demonstrate how easy it is to customize behavior."""
    print("\n=== Customization Example ===")
    
    # Create components with custom settings
    interpolator_config = {
        "newton_raphson_iterations": 50,
        "newton_raphson_tolerance": 1e-15
    }
    
    plot_config = {
        "curve_color": "purple",
        "point_color": "orange",
        "graph_title": "Custom Styled Curve",
        "show_grid": True,
        "curve_line_width": 3
    }
    
    # Create custom curve fitter
    custom_fitter = CurveFitter(
        interpolator_config=interpolator_config,
        plot_config=plot_config
    )
    
    # Fit some data
    points = [(0, 1), (1, 4), (2, 2), (3, 6), (4, 3)]
    x_data, y_data = custom_fitter.fit_from_points(points, show_plot=False)
    
    print(f"Custom fitter generated {len(x_data)} points with higher precision settings")


def demonstrate_component_reuse():
    """Demonstrate how components can be reused and mixed."""
    print("\n=== Component Reuse Example ===")
    
    # Create individual components
    data_loader = DataLoader()
    interpolator = SineInterpolator(newton_raphson_iterations=25)
    plotter = CurvePlotter(config={"curve_color": "red", "point_color": "blue"})
    
    # Use components separately
    points = data_loader.parse_coordinates("(0, 0), (3, 5), (6, 2), (9, 7)")
    print(f"Parsed {len(points)} points from string")
    
    x_interp, y_interp = interpolator.interpolate(points, points_per_segment=100)
    print(f"Interpolated to {len(x_interp)} points")
    
    # Could plot here if needed
    # fig = plotter.plot_curve(x_interp, y_interp, points, show_plot=False)


def demonstrate_extensibility():
    """Show how the OOP structure makes extension easier."""
    print("\n=== Extensibility Example ===")
    
    class CustomInterpolator(SineInterpolator):
        """Example of extending the interpolator with custom behavior."""
        
        def interpolate_with_logging(self, points, points_per_segment=None):
            """Interpolate with progress logging."""
            print(f"Starting interpolation of {len(points)} points...")
            result = self.interpolate(points, points_per_segment)
            print(f"Interpolation complete: {len(result[0])} output points")
            return result
    
    class SmartCurveFitter(CurveFitter):
        """Example of extending the main fitter class."""
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.interpolation_count = 0
        
        def fit_from_points(self, points, **kwargs):
            """Override to add usage tracking."""
            self.interpolation_count += 1
            print(f"Performing interpolation #{self.interpolation_count}")
            return super().fit_from_points(points, **kwargs)
        
        def get_statistics(self):
            """New method to get usage statistics."""
            return {
                "interpolations_performed": self.interpolation_count,
                "last_point_count": len(self._last_points) if self._last_points else 0
            }
    
    # Use the extended classes
    smart_fitter = SmartCurveFitter()
    
    # Perform some interpolations
    points1 = [(0, 1), (2, 3), (4, 2)]
    points2 = [(1, 0), (3, 4), (5, 1), (7, 3)]
    
    smart_fitter.fit_from_points(points1, show_plot=False)
    smart_fitter.fit_from_points(points2, show_plot=False)
    
    stats = smart_fitter.get_statistics()
    print(f"Statistics: {stats}")


def demonstrate_backward_compatibility():
    """Show that the old interface still works."""
    print("\n=== Backward Compatibility ===")
    
    # Import old functions
    from src.main import parse_coords, interpolate, graph
    
    # Use old-style functions
    points = parse_coords("(0, 2), (1, 4), (2, 1), (3, 5)")
    x_data, y_data = interpolate(points)
    
    print(f"Old interface: Parsed {len(points)} points, interpolated to {len(x_data)} points")
    print("Backward compatibility maintained!")


if __name__ == "__main__":
    print("Curve Fitter Object-Oriented Refactoring Demonstration")
    print("=" * 60)
    
    demonstrate_basic_usage()
    demonstrate_customization()
    demonstrate_component_reuse()
    demonstrate_extensibility()
    demonstrate_backward_compatibility()
    
    print("\n" + "=" * 60)
    print("Demonstration complete! The refactored code provides:")
    print("✓ Clean object-oriented structure")
    print("✓ Easy customization and configuration")
    print("✓ Reusable components") 
    print("✓ Extensibility through inheritance")
    print("✓ Full backward compatibility")
    print("✓ Better organization for future expansion")