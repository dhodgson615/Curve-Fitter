"""
Main CurveFitter application class that orchestrates interpolation and visualization.
"""

from src.interpolator import SineInterpolator
from src.data_loader import DataLoader
from src.plotter import CurvePlotter
from src.config import PLOT_CONFIG, SAMPLE_POINTS


class CurveFitter:
    """
    Main application class for curve fitting using sine interpolation.
    
    This class orchestrates the entire process of loading data, performing
    interpolation, and visualizing results.
    """
    
    def __init__(self, interpolator_config=None, plot_config=None):
        """
        Initialize the CurveFitter application.
        
        Args:
            interpolator_config (dict, optional): Configuration for the interpolator
            plot_config (dict, optional): Configuration for the plotter
        """
        # Initialize components
        self.interpolator = SineInterpolator(
            newton_raphson_iterations=interpolator_config.get("newton_raphson_iterations") if interpolator_config else None,
            newton_raphson_tolerance=interpolator_config.get("newton_raphson_tolerance") if interpolator_config else None
        )
        self.data_loader = DataLoader()
        self.plotter = CurvePlotter(config=plot_config)
        
        # Store the last processed data
        self._last_points = None
        self._last_interpolation = None
    
    def fit_from_coordinates(self, coord_string, plot_config=None, show_plot=True):
        """
        Fit a curve from a coordinate string and optionally plot it.
        
        Args:
            coord_string (str): String containing coordinates like "(1, 2), (3, 4)"
            plot_config (dict, optional): Additional plot configuration
            show_plot (bool): Whether to display the plot
            
        Returns:
            Tuple of (x_interpolated, y_interpolated, figure) or 
            (x_interpolated, y_interpolated) if not plotting
        """
        # Parse coordinates
        points = self.data_loader.parse_coordinates(coord_string)
        return self._fit_and_plot(points, plot_config, show_plot)
    
    def fit_from_csv(self, filename, x_column=None, y_column=None, 
                     plot_config=None, show_plot=True):
        """
        Fit a curve from CSV data and optionally plot it.
        
        Args:
            filename (str): Path to the CSV file
            x_column (str, optional): Name of the x-coordinate column
            y_column (str, optional): Name of the y-coordinate column  
            plot_config (dict, optional): Additional plot configuration
            show_plot (bool): Whether to display the plot
            
        Returns:
            Tuple of (x_interpolated, y_interpolated, figure, x_col_name, y_col_name)
            or (x_interpolated, y_interpolated, x_col_name, y_col_name) if not plotting
        """
        # Load data from CSV
        points, x_col, y_col = self.data_loader.load_from_csv(filename, x_column, y_column)
        
        # Fit and plot
        result = self._fit_and_plot(points, plot_config, show_plot)
        
        # Add column names to result
        if show_plot:
            x_data, y_data, fig = result
            return x_data, y_data, fig, x_col, y_col
        else:
            x_data, y_data = result
            return x_data, y_data, x_col, y_col
    
    def fit_from_points(self, points, plot_config=None, show_plot=True):
        """
        Fit a curve from a list of points and optionally plot it.
        
        Args:
            points: List of (x, y) tuples
            plot_config (dict, optional): Additional plot configuration
            show_plot (bool): Whether to display the plot
            
        Returns:
            Tuple of (x_interpolated, y_interpolated, figure) or 
            (x_interpolated, y_interpolated) if not plotting
        """
        return self._fit_and_plot(points, plot_config, show_plot)
    
    def _fit_and_plot(self, points, plot_config=None, show_plot=True):
        """
        Internal method to fit curve and optionally plot.
        
        Args:
            points: List of (x, y) tuples
            plot_config (dict, optional): Additional plot configuration
            show_plot (bool): Whether to display the plot
            
        Returns:
            Tuple of (x_interpolated, y_interpolated, figure) or 
            (x_interpolated, y_interpolated) if not plotting
        """
        # Validate points
        self.data_loader.validate_points(points)
        
        # Perform interpolation
        x_data, y_data = self.interpolator.interpolate(points)
        
        # Store for later use
        self._last_points = points.copy()
        self._last_interpolation = (x_data.copy(), y_data.copy())
        
        if show_plot:
            # Update plot config if provided
            if plot_config:
                self.plotter.update_config(plot_config)
            
            # Create the plot
            fig = self.plotter.plot_curve(x_data, y_data, points, show_plot)
            return x_data, y_data, fig
        else:
            return x_data, y_data
    
    def get_last_points(self):
        """
        Get the last set of points that were processed.
        
        Returns:
            List of (x, y) tuples or None if no points have been processed
        """
        return self._last_points.copy() if self._last_points else None
    
    def get_last_interpolation(self):
        """
        Get the last interpolation result.
        
        Returns:
            Tuple of (x_array, y_array) or None if no interpolation has been done
        """
        if self._last_interpolation:
            x_data, y_data = self._last_interpolation
            return x_data.copy(), y_data.copy()
        return None
    
    def replot_last(self, plot_config=None, show_plot=True):
        """
        Replot the last interpolation with new configuration.
        
        Args:
            plot_config (dict, optional): New plot configuration
            show_plot (bool): Whether to display the plot
            
        Returns:
            matplotlib.figure.Figure or None if no previous data
        """
        if self._last_points is None or self._last_interpolation is None:
            return None
        
        # Update plot config if provided
        if plot_config:
            self.plotter.update_config(plot_config)
        
        x_data, y_data = self._last_interpolation
        return self.plotter.plot_curve(x_data, y_data, self._last_points, show_plot)
    
    def interactive_input(self, prompt=None):
        """
        Get coordinates from user input and fit curve.
        
        Args:
            prompt (str, optional): Input prompt text
            
        Returns:
            Tuple of (x_interpolated, y_interpolated, figure)
        """
        prompt = prompt or self.plotter.config.get("input_prompt", "Coordinates e.g. (1, 2), (3, 4): ")
        coord_string = input(prompt)
        return self.fit_from_coordinates(coord_string, show_plot=True)