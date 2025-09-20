"""
Sine-based interpolation classes for smooth curve fitting.
"""

from numpy import array, cos, linspace, pi, sin
from src.config import INTERPOLATION_CONFIG


class SineInterpolator:
    """
    A class for performing sine-based interpolation between data points.
    
    This interpolator uses half-period sine waves to create smooth curves
    between consecutive points, ensuring the curve passes through all points
    and has zero derivative at each point.
    """
    
    def __init__(self, newton_raphson_iterations=None, newton_raphson_tolerance=None):
        """
        Initialize the SineInterpolator.
        
        Args:
            newton_raphson_iterations (int, optional): Maximum iterations for Newton-Raphson method
            newton_raphson_tolerance (float, optional): Tolerance for Newton-Raphson convergence
        """
        self.newton_raphson_iterations = (
            newton_raphson_iterations or INTERPOLATION_CONFIG["newton_raphson_iterations"]
        )
        self.newton_raphson_tolerance = (
            newton_raphson_tolerance or INTERPOLATION_CONFIG["newton_raphson_tolerance"]
        )
    
    def _sine_function(self, x, x1, x2, y1, y2, n):
        """
        Calculate the sine interpolation function value.
        
        Args:
            x: Input value(s)
            x1, x2: X coordinates of the two points
            y1, y2: Y coordinates of the two points
            n: Phase offset calculated by Newton-Raphson
            
        Returns:
            Interpolated y value(s)
        """
        return (y2 - y1) / 2 * sin(pi * (x - x2 - n) / (x2 - x1)) + (y1 + y2) / 2
    
    def _newton_raphson(self, x1, x2, y1, y2):
        """
        Use Newton-Raphson method to find the phase offset n.
        
        Args:
            x1, x2: X coordinates of the two points
            y1, y2: Y coordinates of the two points
            
        Returns:
            Phase offset n
            
        Raises:
            ValueError: If derivative hits zero or points are identical
        """
        # Check for identical x coordinates
        if x2 == x1:
            raise ValueError("Newton–Raphson derivative hit zero")
        
        n = 0.0
        for _ in range(self.newton_raphson_iterations):
            fn = (y2 - y1) / 2 * sin(pi * n / (x2 - x1)) + (y1 + y2) / 2 - y1
            fp = (y2 - y1) / 2 * cos(pi * n / (x2 - x1)) * pi / (x2 - x1)
            
            if abs(fn) < self.newton_raphson_tolerance:
                break
            if fp == 0:
                raise ValueError("Newton–Raphson derivative hit zero")
            
            n -= fn / fp
        
        return n
    
    def interpolate(self, points, points_per_segment=None):
        """
        Interpolate between the given points using sine functions.
        
        Args:
            points: List of (x, y) tuples representing the points to interpolate
            points_per_segment (int, optional): Number of points per segment
            
        Returns:
            Tuple of (x_array, y_array) containing interpolated points
        """
        points_per_segment = points_per_segment or INTERPOLATION_CONFIG["points_per_segment"]
        points = sorted(points)
        xs_out, ys_out = [], []
        
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # Generate x values for this segment
            seg_x = linspace(x1, x2, points_per_segment, endpoint=False)
            
            # Calculate phase offset using Newton-Raphson
            n = self._newton_raphson(x1, x2, y1, y2)
            
            # Calculate y values using sine function
            seg_y = self._sine_function(seg_x, x1, x2, y1, y2, n)
            
            xs_out.extend(seg_x)
            ys_out.extend(seg_y)
        
        # Add the final point
        xs_out.append(points[-1][0])
        ys_out.append(points[-1][1])
        
        return array(xs_out), array(ys_out)