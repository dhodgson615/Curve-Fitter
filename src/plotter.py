"""
Curve plotting and visualization utilities.
"""

import matplotlib.pyplot as plt
from src.config import PLOT_CONFIG


class CurvePlotter:
    """
    A class for plotting interpolated curves and data points.
    
    Handles all matplotlib visualization with configurable styling.
    """
    
    def __init__(self, config=None):
        """
        Initialize the CurvePlotter.
        
        Args:
            config (dict, optional): Plot configuration dictionary.
                                   If None, uses default PLOT_CONFIG.
        """
        self.config = PLOT_CONFIG.copy()
        if config:
            self.config.update(config)
    
    def update_config(self, config):
        """
        Update the plot configuration.
        
        Args:
            config (dict): Configuration dictionary to merge with current config
        """
        if config:
            self.config.update(config)
    
    def plot_curve(self, x_data, y_data, original_points, show_plot=None):
        """
        Plot the interpolated curve and original data points.
        
        Args:
            x_data: Array of x coordinates for the interpolated curve
            y_data: Array of y coordinates for the interpolated curve
            original_points: List of (x, y) tuples representing original data points
            show_plot (bool, optional): Whether to display the plot. 
                                      If None, uses config setting.
                                      
        Returns:
            matplotlib.figure.Figure: The created figure object
        """
        # Set up the plot style
        plt.style.use(self.config["plot_style"])
        fig = plt.figure(figsize=self.config["figsize"])
        
        # Plot the interpolated curve
        plt.plot(
            x_data,
            y_data,
            label=self.config["curve_label"],
            color=self.config["curve_color"],
            linestyle=self.config["curve_line_style"],
            linewidth=self.config["curve_line_width"],
            alpha=self.config["alpha"],
        )
        
        # Plot the original points
        if original_points:
            x_points, y_points = zip(*original_points)
            plt.scatter(
                x_points,
                y_points,
                color=self.config["point_color"],
                marker=self.config["point_marker"],
                label=self.config["point_label"],
                alpha=self.config["alpha"],
            )
        
        # Add labels and customize
        plt.title(self.config["graph_title"])
        
        if self.config["x_label"]:
            plt.xlabel(self.config["x_label"])
        
        if self.config["y_label"]:
            plt.ylabel(self.config["y_label"])
        
        plt.legend()
        plt.grid(self.config["show_grid"])
        
        # Show the plot if requested
        show = show_plot if show_plot is not None else self.config["show_plot"]
        if show:
            plt.show()
        
        return fig
    
    def get_config(self):
        """
        Get the current plot configuration.
        
        Returns:
            dict: Current configuration dictionary
        """
        return self.config.copy()
    
    def set_style(self, style_name):
        """
        Set the matplotlib style.
        
        Args:
            style_name (str): Name of the matplotlib style to use
        """
        self.config["plot_style"] = style_name
    
    def set_colors(self, curve_color=None, point_color=None):
        """
        Set the colors for curve and points.
        
        Args:
            curve_color (str, optional): Color for the interpolated curve
            point_color (str, optional): Color for the original points
        """
        if curve_color:
            self.config["curve_color"] = curve_color
        if point_color:
            self.config["point_color"] = point_color
    
    def set_labels(self, title=None, x_label=None, y_label=None, 
                   curve_label=None, point_label=None):
        """
        Set the labels for the plot.
        
        Args:
            title (str, optional): Plot title
            x_label (str, optional): X-axis label
            y_label (str, optional): Y-axis label
            curve_label (str, optional): Legend label for the curve
            point_label (str, optional): Legend label for the points
        """
        if title:
            self.config["graph_title"] = title
        if x_label:
            self.config["x_label"] = x_label
        if y_label:
            self.config["y_label"] = y_label
        if curve_label:
            self.config["curve_label"] = curve_label
        if point_label:
            self.config["point_label"] = point_label