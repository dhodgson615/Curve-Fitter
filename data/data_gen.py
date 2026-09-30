from argparse import ArgumentParser
from typing import Any, Optional, Union

from numpy import array, dtype, float64, generic, linspace, ndarray, pi, sin
from numpy.random import normal, seed, uniform
from numpy.typing import NDArray
from pandas import DataFrame


def _reg_pts(period_hours: float, num_points: int) -> NDArray[float64]:
    return linspace(0, period_hours, num_points, dtype=float64)


def _rand_pts(period_hours: float, num_points: int) -> NDArray[float64]:
    return array(
        sorted(
            float(x) for x in uniform(0, period_hours, max(0, num_points - 1))
        )
        + [period_hours],
        dtype=float64,
    )


def _make_day_segments(period_hours: float) -> dict[str, tuple[float, float]]:
    return {
        key: (
            (value[0] * (period_hours / 24), value[1] * (period_hours / 24))
            if period_hours != 24
            else value
        )
        for key, value in {
            "early_morning": (0, 6),
            "morning": (6, 12),
            "afternoon": (12, 18),
            "night": (18, 24),
        }.items()
    }


def _get_pts_per_seg(
    day_segments: dict[str, tuple[float, float]],
    weights: dict[str, float],
    num_points: int,
) -> dict[str, int]:
    points_per_segment = {
        segment: max(1, int(weights.get(segment, 0) * num_points))
        for segment in day_segments
    }

    diff = num_points - sum(points_per_segment.values())

    if diff != 0:
        keys = list(points_per_segment.keys())

        for i in range(abs(diff)):
            points_per_segment[keys[i % len(keys)]] += 1 if diff > 0 else -1

    return points_per_segment


def _weighted_pts(period_hours: float, n_points: int) -> NDArray[float64]:
    return array(
        sorted(
            [
                float(x)
                for segments in [_make_day_segments(period_hours)]
                for points_per_segment in [
                    _get_pts_per_seg(
                        segments,
                        {
                            "early_morning": 0.15,
                            "morning": 0.3,
                            "afternoon": 0.3,
                            "night": 0.25,
                        },
                        n_points,
                    )
                ]
                for segment, (start, end) in segments.items()
                for x in sorted(
                    uniform(start, end, points_per_segment.get(segment, 0))
                )
            ]
        ),
        dtype=float64,
    )


def gen_t_pts(
    period_hrs: float = 24,
    n_pts: int = 25,
    dist: str = "regular",  # 'regular', 'random', 'weighted'
) -> Union[
    ndarray[tuple[Any, ...], dtype[float64]],
    ndarray[
        tuple[Any, ...], dtype[generic[Any]]
    ],  # TODO: narrow type and replace `Any`
]:
    """Generate time points based on specified interval type (drop-in replacement)."""
    assert dist in (
        "regular",
        "random",
        "weighted",
    ), f"Unknown distribution type: {dist}"

    return (
        _reg_pts(period_hrs, n_pts)
        if dist == "regular"
        else (
            _rand_pts(period_hrs, n_pts)
            if dist == "random"
            else (
                _weighted_pts(period_hrs, n_pts)
                if dist == "weighted"
                else array([], dtype=float64)
            )
        )
    )


def gen_temps(
    hours: NDArray[float64],
    base_temp: float = 18,
    amplitude: float = 7,
    period_hours: float = 24,
    noise_std: float = 1.2,
) -> NDArray[float64]:
    """Generate temperature values for given hours"""
    return (
        base_temp
        + amplitude * sin(2 * pi * hours / period_hours - pi / 2)
        + normal(0, noise_std, hours.size)
    )


def generate_and_save(
    period_hours: float = 24,
    num_points: int = 25,
    interval_type: str = "regular",
    base_temp: float = 18,
    amplitude: float = 7,
    noise_std: float = 1.2,
    random_seed: Optional[int] = None,
    output_file: str = "data_points.csv",
) -> DataFrame:
    """Generate data and save to CSV file"""
    if random_seed is not None:
        seed(random_seed)

    hours = gen_t_pts(period_hours, num_points, interval_type)
    temps = gen_temps(hours, base_temp, amplitude, period_hours, noise_std)
    data = DataFrame({"Time (hours)": hours, "Temperature (°C)": temps})
    data.to_csv(output_file, index=False)

    print(
        f"CSV file '{output_file}' created with {len(hours)} "
        f"temperature data points across {period_hours} hours"
    )

    return data


def generate() -> None:
    """Parse command line arguments and generate data"""
    parser = ArgumentParser(description="Generate synthetic temperature data")

    parser.add_argument(
        "--period",
        type=float,
        default=24,
        help="Total period in hours (default: 24)",
    )

    parser.add_argument(
        "--points",
        type=int,
        default=25,
        help="Number of data points (default: 25)",
    )

    parser.add_argument(
        "--intervals",
        type=str,
        choices=["regular", "random", "weighted"],
        default="regular",
        help="Interval distribution type (default: regular)",
    )

    parser.add_argument(
        "--base-temp",
        type=float,
        default=18,
        help="Base temperature in °C (default: 18)",
    )

    parser.add_argument(
        "--amplitude",
        type=float,
        default=7,
        help="Temperature amplitude in °C (default: 7)",
    )

    parser.add_argument(
        "--noise",
        type=float,
        default=1.2,
        help="Standard deviation of noise (default: 1.2)",
    )

    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed (default: None)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="data_points.csv",
        help="Output CSV filename (default: data_points.csv)",
    )

    args = parser.parse_args()

    generate_and_save(
        period_hours=args.period,
        num_points=args.points,
        interval_type=args.intervals,
        base_temp=args.base_temp,
        amplitude=args.amplitude,
        noise_std=args.noise,
        random_seed=args.seed,
        output_file=args.output,
    )


if __name__ == "__main__":
    generate()
