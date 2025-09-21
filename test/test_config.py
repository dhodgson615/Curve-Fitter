import src.config


class TestConfig:
    def test_plot_config_exists(self) -> None:
        # Test that PLOT_CONFIG exists and has expected keys
        assert isinstance(PLOT_CONFIG, dict)
        essential_keys = [
            "plot_style",
            "figsize",
            "curve_label",
            "curve_color",
            "curve_line_style",
            "curve_line_width",
            "point_color",
            "point_marker",
            "point_label",
            "graph_title",
            "x_label",
            "y_label",
            "show_grid",
            "show_plot",
            "alpha",
        ]
        for key in essential_keys:
            assert key in PLOT_CONFIG

    def test_sample_points(self) -> None:
        # Test that SAMPLE_POINTS contains valid point data
        assert isinstance(SAMPLE_POINTS, list)
        assert len(SAMPLE_POINTS) > 0

        for point in SAMPLE_POINTS:
            assert isinstance(point, tuple)
            assert len(point) == 2
            assert isinstance(point[0], (int, float))
            assert isinstance(point[1], (int, float))

    def test_csv_file_defined(self) -> None:
        # Check that CSV_FILE is defined
        assert isinstance(CSV_FILE, str)
        assert CSV_FILE.endswith(".csv")

    def test_csv_plot_config(self) -> None:
        # Test that CSV_PLOT_CONFIG exists and has expected keys
        assert isinstance(CSV_PLOT_CONFIG, dict)
        essential_keys = [
            "plot_style",
            "figsize",
            "curve_label",
            "point_color",
            "point_label",
            "show_grid",
        ]
        for key in essential_keys:
            assert key in CSV_PLOT_CONFIG

    def test_sample_plot_config(self) -> None:
        # Test that SAMPLE_PLOT_CONFIG exists and has expected keys
        assert isinstance(src.config.SAMPLE_PLOT_CONFIG, dict)
        
        essential_keys = [
            "plot_style",
            "figsize",
            "curve_label",
            "point_color",
            "point_label",
            "graph_title",
            "show_grid",
            "regenerate_points",
        ]
        for key in essential_keys:
            assert key in src.config.SAMPLE_PLOT_CONFIG

        # Check that regenerate_points is a boolean
        assert isinstance(
            src.config.SAMPLE_PLOT_CONFIG["regenerate_points"], bool
        )

    def test_interpolation_config(self) -> None:
        # Test that INTERPOLATION_CONFIG exists and has expected keys
        assert isinstance(src.config.INTERPOLATION_CONFIG, dict)
        
        essential_keys = [
            "points_per_segment",
            "newton_raphson_iterations",
            "newton_raphson_tolerance",
        ]

        for key in essential_keys:
            assert key in src.config.INTERPOLATION_CONFIG

        # Check numeric values are appropriate
        assert src.config.INTERPOLATION_CONFIG["points_per_segment"] > 0
        assert src.config.INTERPOLATION_CONFIG["newton_raphson_iterations"] > 0
        assert src.config.INTERPOLATION_CONFIG["newton_raphson_tolerance"] > 0
