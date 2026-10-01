"""Tests for the main module."""

from math import isclose
from os import path, remove  # TODO: Use pathlib.Path instead of os.path
from tempfile import NamedTemporaryFile
from typing import TypeAlias

from pandas import DataFrame
from pytest import raises

from lib import (DEFAULT_NEWTON_TOLERANCE, adjust_n, f, find_phase_shift,
                 half_sine, interpolate, load_points_from_csv)

Point: TypeAlias = tuple[float, float]


class TestHalfSine:
    """Tests for the half_sine mathematical function."""

    def test_half_sine_basic_midpoint(self) -> None:
        """Test calculation at midpoint between two coordinates."""
        # For x1=0, y1=0, x2=2, y2=10, n=0:
        # phase = pi * (1 - 2 - 0) / 2 = -pi / 2
        # sin(-pi/2) = -1 -> y = (0 + 10 + 10*(-1)) / 2 = 0
        val = half_sine(x=1.0, x1=0.0, x2=2.0, y1=0.0, y2=10.0, n=0.0)
        assert isclose(val, 0.0, abs_tol=1e-7)

    def test_half_sine_alias(self) -> None:
        """Verify backwards compatibility alias `f` matches `half_sine`."""
        args = (1.5, 0.0, 3.0, 2.0, 8.0, -0.5)
        assert half_sine(*args) == f(*args)


class TestFindPhaseShift:
    """Tests for Newton-Raphson phase shift calculation."""

    def test_find_phase_shift_convergence(self) -> None:
        """Ensure phase shift yields expected y1 value at x1."""
        x1, y1 = 0.0, 5.0
        x2, y2 = 4.0, 15.0

        n = find_phase_shift(x1, x2, y1, y2)
        y_calc = half_sine(x1, x1, x2, y1, y2, n)

        assert isclose(y_calc, y1, abs_tol=DEFAULT_NEWTON_TOLERANCE)

    def test_find_phase_shift_identical_x_raises_assertion(self) -> None:
        """Ensure passing identical x1 and x2 triggers an AssertionError."""
        with raises(AssertionError, match="x1 and x2 must be different"):
            find_phase_shift(2.0, 2.0, 5.0, 10.0)

    def test_find_phase_shift_alias(self) -> None:
        """Verify backwards compatibility alias `adjust_n` matches `find_phase_shift`."""
        args = (0.0, 2.0, 1.0, 5.0)
        assert find_phase_shift(*args) == adjust_n(*args)


class TestInterpolate:
    """Tests for the point list interpolation pipeline."""

    def test_interpolate_passes_through_given_points(self) -> None:
        """Verify that the generated curve exact-matches all key input points."""
        points = [(0.0, 5.0), (2.0, 0.0), (4.0, 10.0)]
        pts_per_seg = 50

        curve = interpolate(points, points_per_segment=pts_per_seg)

        # Check start point of segment 1
        assert isclose(curve[0][0], 0.0, abs_tol=1e-6)
        assert isclose(curve[0][1], 5.0, abs_tol=1e-6)

        # Check start point of segment 2 (index: pts_per_seg)
        assert isclose(curve[pts_per_seg][0], 2.0, abs_tol=1e-6)
        assert isclose(curve[pts_per_seg][1], 0.0, abs_tol=1e-6)

        # Check final point
        assert isclose(curve[-1][0], 4.0, abs_tol=1e-6)
        assert isclose(curve[-1][1], 10.0, abs_tol=1e-6)

    def test_interpolate_length_calculation(self) -> None:
        """Verify length of output curve matches expected segment count."""
        points = [(0.0, 0.0), (1.0, 2.0), (2.0, 0.0)]
        pts_per_seg = 10
        curve = interpolate(points, points_per_segment=pts_per_seg)

        # Expected total points = (number_of_segments * pts_per_seg) + 1
        expected_len = (len(points) - 1) * pts_per_seg + 1
        assert len(curve) == expected_len

    def test_interpolate_unsorted_input(self) -> None:
        """Ensure input points are automatically sorted by x-coordinate."""
        unsorted_pts = [(4.0, 10.0), (0.0, 5.0), (2.0, 0.0)]
        curve = interpolate(unsorted_pts)

        # First x should be 0.0, last x should be 4.0
        assert isclose(curve[0][0], 0.0)
        assert isclose(curve[-1][0], 4.0)

    def test_interpolate_fewer_than_two_points_raises(self) -> None:
        """Verify error when attempting to interpolate fewer than 2 points."""
        with raises(AssertionError, match="At least 2 points are required"):
            interpolate([(1.0, 2.0)])


class TestLoadPointsFromCSV:
    """Tests for reading point datasets from CSV files."""

    def test_load_points_from_csv_default_columns(self) -> None:
        """Test loading data using implicit first/second columns."""
        df = DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})

        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name

        try:
            points, x_col, y_col = load_points_from_csv(tmp_path)
            assert points == [(1.0, 4.0), (2.0, 5.0), (3.0, 6.0)]
            assert x_col == "x"
            assert y_col == "y"

        finally:
            if path.exists(tmp_path):
                remove(tmp_path)

    def test_load_points_from_csv_explicit_columns(self) -> None:
        """Test loading data using specific column selection."""
        df = DataFrame(
            {
                "time": [0.0, 10.0],
                "temp": [20.0, 25.0],
                "pressure": [101.3, 101.5],
            }
        )

        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name

        try:
            points, x_col, y_col = load_points_from_csv(
                tmp_path, x_column="time", y_column="pressure"
            )

            assert points == [(0.0, 101.3), (10.0, 101.5)]
            assert x_col == "time"
            assert y_col == "pressure"

        finally:
            if path.exists(tmp_path):
                remove(tmp_path)

    def test_load_points_from_csv_insufficient_columns_raises(self) -> None:
        """Verify error when CSV contains fewer than two columns."""
        df = DataFrame({"single_col": [1.0, 2.0, 3.0]})

        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name

        try:
            with raises(
                AssertionError,
                match="CSV file must contain at least two columns",
            ):
                load_points_from_csv(tmp_path)

        finally:
            if path.exists(tmp_path):
                remove(tmp_path)
