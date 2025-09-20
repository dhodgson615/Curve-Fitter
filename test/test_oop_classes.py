"""
Tests for the new object-oriented classes in the curve fitter.
"""

import pytest
import numpy as np
import matplotlib.figure
import tempfile
import os
import pandas as pd

from src.interpolator import SineInterpolator
from src.data_loader import DataLoader
from src.plotter import CurvePlotter
from src.curve_fitter import CurveFitter


class TestSineInterpolator:
    @pytest.fixture
    def interpolator(self):
        return SineInterpolator()
    
    @pytest.fixture
    def sample_points(self):
        return [(0, 1), (2, 3), (4, 2), (6, 5)]
    
    def test_initialization(self):
        # Test default initialization
        interpolator = SineInterpolator()
        assert interpolator.newton_raphson_iterations == 30
        assert interpolator.newton_raphson_tolerance == 1e-12
        
        # Test custom initialization
        custom_interpolator = SineInterpolator(
            newton_raphson_iterations=50,
            newton_raphson_tolerance=1e-10
        )
        assert custom_interpolator.newton_raphson_iterations == 50
        assert custom_interpolator.newton_raphson_tolerance == 1e-10
    
    def test_sine_function(self, interpolator):
        # Test the sine function with known values
        result = interpolator._sine_function(1, 0, 2, 1, 3, 0)
        assert isinstance(result, (int, float, np.number))
        
        # Test with arrays
        x_array = np.array([0, 1, 2])
        result_array = interpolator._sine_function(x_array, 0, 2, 1, 3, 0)
        assert isinstance(result_array, np.ndarray)
        assert len(result_array) == len(x_array)
    
    def test_newton_raphson(self, interpolator):
        # Test normal case
        n = interpolator._newton_raphson(0, 2, 1, 3)
        assert isinstance(n, float)
        
        # Test error case with identical points
        with pytest.raises(ValueError, match="Newton–Raphson derivative hit zero"):
            interpolator._newton_raphson(1, 1, 2, 3)
    
    def test_interpolate(self, interpolator, sample_points):
        x_data, y_data = interpolator.interpolate(sample_points)
        
        # Check that we get numpy arrays
        assert isinstance(x_data, np.ndarray)
        assert isinstance(y_data, np.ndarray)
        
        # Check that arrays have the same length
        assert len(x_data) == len(y_data)
        
        # Check that interpolation passes through original points
        for orig_x, orig_y in sample_points:
            # Find the closest interpolated point
            closest_idx = np.argmin(np.abs(x_data - orig_x))
            assert np.isclose(x_data[closest_idx], orig_x, atol=1e-10)
            assert np.isclose(y_data[closest_idx], orig_y, atol=1e-5)


class TestDataLoader:
    @pytest.fixture
    def data_loader(self):
        return DataLoader()
    
    def test_parse_coordinates(self, data_loader):
        # Test valid coordinate string
        coord_string = "(1, 2), (3, 4), (5.5, 6.7)"
        points = data_loader.parse_coordinates(coord_string)
        
        expected = [(1.0, 2.0), (3.0, 4.0), (5.5, 6.7)]
        assert points == expected
        
        # Test empty string
        assert data_loader.parse_coordinates("") == []
        
        # Test malformed coordinates
        assert data_loader.parse_coordinates("invalid") == []
    
    def test_load_from_csv(self, data_loader):
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("x,y\n1,2\n3,4\n5,6\n")
            temp_filename = f.name
        
        try:
            points, x_col, y_col = data_loader.load_from_csv(temp_filename)
            
            assert points == [(1, 2), (3, 4), (5, 6)]
            assert x_col == "x"
            assert y_col == "y"
        finally:
            os.unlink(temp_filename)
    
    def test_load_from_csv_custom_columns(self, data_loader):
        # Create temporary CSV file with custom column names
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("time,temperature,pressure\n0,20,1013\n1,21,1012\n")
            temp_filename = f.name
        
        try:
            points, x_col, y_col = data_loader.load_from_csv(
                temp_filename, x_column="time", y_column="temperature"
            )
            
            assert points == [(0, 20), (1, 21)]
            assert x_col == "time"
            assert y_col == "temperature"
        finally:
            os.unlink(temp_filename)
    
    def test_load_from_csv_errors(self, data_loader):
        # Test file not found
        with pytest.raises(FileNotFoundError):
            data_loader.load_from_csv("nonexistent.csv")
        
        # Test insufficient columns
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("x\n1\n2\n")
            temp_filename = f.name
        
        try:
            with pytest.raises(ValueError, match="must have at least 2 columns"):
                data_loader.load_from_csv(temp_filename)
        finally:
            os.unlink(temp_filename)
    
    def test_validate_points(self, data_loader):
        # Test valid points
        valid_points = [(1, 2), (3, 4)]
        assert data_loader.validate_points(valid_points) == True
        
        # Test invalid inputs
        with pytest.raises(ValueError, match="Points must be a list"):
            data_loader.validate_points("not a list")
        
        with pytest.raises(ValueError, match="At least 2 points are required"):
            data_loader.validate_points([(1, 2)])
        
        with pytest.raises(ValueError, match="must be a tuple or list of length 2"):
            data_loader.validate_points([(1, 2, 3), (4, 5)])
        
        with pytest.raises(ValueError, match="contains non-numeric values"):
            data_loader.validate_points([(1, 2), ("a", "b")])


class TestCurvePlotter:
    @pytest.fixture
    def plotter(self):
        return CurvePlotter(config={"show_plot": False})
    
    @pytest.fixture
    def sample_data(self):
        x_data = np.linspace(0, 10, 100)
        y_data = np.sin(x_data)
        original_points = [(0, 0), (5, -1), (10, 0)]
        return x_data, y_data, original_points
    
    def test_initialization(self):
        # Test default initialization
        plotter = CurvePlotter()
        assert "plot_style" in plotter.config
        
        # Test custom config
        custom_config = {"curve_color": "red", "show_plot": False}
        plotter = CurvePlotter(config=custom_config)
        assert plotter.config["curve_color"] == "red"
        assert plotter.config["show_plot"] == False
    
    def test_plot_curve(self, plotter, sample_data):
        x_data, y_data, original_points = sample_data
        
        fig = plotter.plot_curve(x_data, y_data, original_points, show_plot=False)
        
        assert isinstance(fig, matplotlib.figure.Figure)
        
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_configuration_methods(self, plotter):
        # Test update_config
        plotter.update_config({"curve_color": "green"})
        assert plotter.config["curve_color"] == "green"
        
        # Test set_colors
        plotter.set_colors(curve_color="blue", point_color="red")
        assert plotter.config["curve_color"] == "blue"
        assert plotter.config["point_color"] == "red"
        
        # Test set_labels
        plotter.set_labels(title="Test Title", x_label="X", y_label="Y")
        assert plotter.config["graph_title"] == "Test Title"
        assert plotter.config["x_label"] == "X"
        assert plotter.config["y_label"] == "Y"


class TestCurveFitter:
    @pytest.fixture
    def curve_fitter(self):
        return CurveFitter(plot_config={"show_plot": False})
    
    @pytest.fixture
    def sample_points(self):
        return [(0, 1), (2, 3), (4, 2), (6, 5)]
    
    def test_initialization(self):
        fitter = CurveFitter()
        
        assert isinstance(fitter.interpolator, SineInterpolator)
        assert isinstance(fitter.data_loader, DataLoader)
        assert isinstance(fitter.plotter, CurvePlotter)
    
    def test_fit_from_points(self, curve_fitter, sample_points):
        x_data, y_data, fig = curve_fitter.fit_from_points(sample_points, show_plot=True)
        
        assert isinstance(x_data, np.ndarray)
        assert isinstance(y_data, np.ndarray)
        assert isinstance(fig, matplotlib.figure.Figure)
        
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_fit_from_coordinates(self, curve_fitter):
        coord_string = "(0, 1), (2, 3), (4, 2)"
        x_data, y_data, fig = curve_fitter.fit_from_coordinates(coord_string)
        
        assert isinstance(x_data, np.ndarray)
        assert isinstance(y_data, np.ndarray)
        assert isinstance(fig, matplotlib.figure.Figure)
        
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_fit_from_csv(self, curve_fitter):
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("x,y\n0,1\n2,3\n4,2\n")
            temp_filename = f.name
        
        try:
            x_data, y_data, fig, x_col, y_col = curve_fitter.fit_from_csv(temp_filename)
            
            assert isinstance(x_data, np.ndarray)
            assert isinstance(y_data, np.ndarray)
            assert isinstance(fig, matplotlib.figure.Figure)
            assert x_col == "x"
            assert y_col == "y"
            
            # Clean up
            import matplotlib.pyplot as plt
            plt.close(fig)
        finally:
            os.unlink(temp_filename)
    
    def test_get_last_methods(self, curve_fitter, sample_points):
        # Initially should be None
        assert curve_fitter.get_last_points() is None
        assert curve_fitter.get_last_interpolation() is None
        
        # After fitting
        curve_fitter.fit_from_points(sample_points, show_plot=False)
        
        last_points = curve_fitter.get_last_points()
        last_interp = curve_fitter.get_last_interpolation()
        
        assert last_points == sample_points
        assert last_interp is not None
        assert len(last_interp) == 2  # x_data, y_data
    
    def test_replot_last(self, curve_fitter, sample_points):
        # Should return None if no previous data
        assert curve_fitter.replot_last() is None
        
        # Fit some data first
        curve_fitter.fit_from_points(sample_points, show_plot=False)
        
        # Now replot should work
        fig = curve_fitter.replot_last(show_plot=False)
        assert isinstance(fig, matplotlib.figure.Figure)
        
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)