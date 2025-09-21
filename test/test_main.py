import os
import re
import tempfile
from unittest import mock

import matplotlib
import numpy as np
import pandas as pd
import pytest

import src.main

matplotlib.use("Agg")  # Set matplotlib to use non-interactive backend


class TestMainFunctions:
    @pytest.fixture
    def sample_points(self) -> list[tuple[float, float]]:
        return [(0, 5), (2, 0), (4, 10), (6, 5), (8, 0)]

    def test_parse_coords(self) -> None:
        # Test basic coordinate parsing
        assert src.main.parse_coords("(1, 2), (3, 4)") == [
            (1.0, 2.0),
            (3.0, 4.0),
        ]

        # Test with irregular spacing
        assert src.main.parse_coords("(1,2),(3,4)") == [(1.0, 2.0), (3.0, 4.0)]
        assert src.main.parse_coords("( 1 , 2 ), ( 3 , 4 )") == [
            (1.0, 2.0),
            (3.0, 4.0),
        ]

        # Test with negative and decimal values
        assert src.main.parse_coords("(-1.5, -2.3), (3.7, 4.1)") == [
            (-1.5, -2.3),
            (3.7, 4.1),
        ]

        # Test regex pattern directly
        matches = re.findall(src.main.COORD_REGEX, "(1, 2), (3, 4)")

        assert matches == [("1", "2"), ("3", "4")]

    def test_f_function(self) -> None:
        x1, x2 = 0, 2
        y1, y2 = 0, 10

        # Calculate the adjustment needed to make the curve pass through points
        n = src.main.newton_raphson(x1, x2, y1, y2)

        # Test that the function returns y1 at x1
        assert np.isclose(src.main.f(x1, x1, x2, y1, y2, n), y1)

        # Test that the function returns y2 at x2
        assert np.isclose(src.main.f(x2, x1, x2, y1, y2, n), y2)

        # Test case 2: Without adjustment (n=0), midpoint should return y1
        mid_x = (x1 + x2) / 2
        assert np.isclose(f(mid_x, x1, x2, y1, y2, 0), y1)

        # Test case 3: Negative values
        x1, x2 = -3, -1
        y1, y2 = -5, -2
        n = newton_raphson(x1, x2, y1, y2)

        assert np.isclose(f(x1, x1, x2, y1, y2, n), y1)
        assert np.isclose(f(x2, x1, x2, y1, y2, n), y2)

        # Test case 4: Mixed positive and negative values
        x1, x2 = -5, 5
        y1, y2 = -10, 10
        n = newton_raphson(x1, x2, y1, y2)

        assert np.isclose(f(x1, x1, x2, y1, y2, n), y1)
        assert np.isclose(f(x2, x1, x2, y1, y2, n), y2)

        # Test case 5: When y1=y2, function should produce a flat line
        x1, x2 = 0, 10
        y1, y2 = 5, 5

        assert np.isclose(f(3, x1, x2, y1, y2, 0), 5)
        assert np.isclose(f(7, x1, x2, y1, y2, 0), 5)

    def test_newton_raphson(self) -> None:
        # Test Newton-Raphson solver for simple cases
        x1, x2 = 0, 2
        y1, y2 = 0, 10

        # The n value should make f(x1) = y1
        n = newton_raphson(x1, x2, y1, y2)
        result = f(x1, x1, x2, y1, y2, n)
        assert np.isclose(result, y1)

        # Test with different values
        x1, x2 = 1, 3
        y1, y2 = 5, 15
        n = newton_raphson(x1, x2, y1, y2)
        result = f(x1, x1, x2, y1, y2, n)
        assert np.isclose(result, y1)

    def test_newton_raphson_zero_derivative(self) -> None:
        # Test when derivative hits zero
        x1, x2 = (0, 0)  # Should cause division by zero in derivative
        y1, y2 = 0, 10

        with pytest.raises(
            ValueError, match="Newton–Raphson derivative hit zero"
        ):
            newton_raphson(x1, x2, y1, y2)

    def test_interpolate(
        self, sample_points: list[tuple[float, float]]
    ) -> None:
        # Test point interpolation
        x_interp, y_interp = interpolate(sample_points, pts_per_seg=10)

        # Check that interpolated arrays have correct length
        expected_length = (len(sample_points) - 1) * 10 + 1
        assert len(x_interp) == expected_length
        assert len(y_interp) == expected_length

        # Check that the interpolated points include original points
        x_original, y_original = zip(*sample_points)
        assert np.isclose(x_interp[0], x_original[0])
        assert np.isclose(y_interp[0], y_original[0])
        assert np.isclose(x_interp[-1], x_original[-1])
        assert np.isclose(y_interp[-1], y_original[-1])

    def test_load_points_from_csv(self) -> None:
        # Create a test CSV file
        data = pd.DataFrame({"x": [0, 1, 2, 3, 4], "y": [5, 4, 3, 2, 1]})

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            try:
                data.to_csv(tmp.name, index=False)

                # Test loading with default column names
                points, x_col, y_col = load_points_from_csv(tmp.name)
                assert len(points) == 5
                assert x_col == "x"
                assert y_col == "y"
                assert points[0] == (0, 5)
                assert points[-1] == (4, 1)

                # Test with explicit column names
                points, x_col, y_col = load_points_from_csv(tmp.name, "x", "y")
                assert x_col == "x"
                assert y_col == "y"

            finally:
                os.unlink(tmp.name)

    @mock.patch("matplotlib.pyplot.show")
    def test_graph(
        self,
        mock_show: mock.MagicMock,
        sample_points: list[tuple[float, float]],
    ) -> None:
        # Test graph generation
        fig = src.main.graph(points=sample_points, config={"show_plot": False})

        # Check that a figure was created
        assert isinstance(fig, matplotlib.figure.Figure)

        # Check that show was not called (we set show_plot=False)
        mock_show.assert_not_called()

        # Test with show_plot=True
        fig = src.main.graph(points=sample_points, config={"show_plot": True})
        mock_show.assert_called_once()

        # Clean up
        matplotlib.pyplot.close(fig)


import tempfile
