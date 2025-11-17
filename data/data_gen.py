from argparse import ArgumentParser
from typing import Optional

from numpy import array, float64, linspace, pi, sin
from numpy.random import normal, seed, uniform
from numpy.typing import NDArray
from pandas import DataFrame


def generate_time_points(
    period_hours: float = 24,
    num_points: int = 25,
    interval_type: str = "regular",  # 'regular', 'random', 'weighted'
) -> NDArray[float64]:
    """Generate time points based on specified interval type"""
    assert interval_type in [
        "regular",
        "random",
        "weighted",
    ], f"Unknown interval type: {interval_type}"

    if interval_type == "regular":
        return linspace(0, period_hours, num_points, dtype=float64)

    elif interval_type == "random":
        random_values = uniform(0, period_hours, num_points - 1)
        random_values_list = [float(x) for x in random_values]
        random_times = sorted(random_values_list)
        return array(random_times + [period_hours], dtype=float64)

    elif interval_type == "weighted":
        # More readings during day, fewer at night
        day_segs: dict[str, tuple[float, float]] = {
            "early_morning": (0, 6),  # Fewer readings
            "morning": (6, 12),  # More readings
            "afternoon": (12, 18),  # More readings
            "night": (18, 24),  # Fewer readings
        }

        if period_hours != 24:
            scale = period_hours / 24

            day_segs = {
                k: (v[0] * scale, v[1] * scale) for k, v in day_segs.items()
            }

        weights: dict[str, float] = {
            "early_morning": 0.15,
            "morning": 0.3,
            "afternoon": 0.3,
            "night": 0.25,
        }

        pts_per_seg = {
            seg: max(1, int(weights[seg] * num_points)) for seg in day_segs
        }

        diff = num_points - sum(pts_per_seg.values())

        if diff != 0:
            keys = list(pts_per_seg.keys())

            for i in range(abs(diff)):
                pts_per_seg[keys[i % len(keys)]] += 1 if diff > 0 else -1

        return array(
            sorted(
                [
                    float(x)
                    for seg, (start, end) in day_segs.items()
                    if pts_per_seg[seg] > 0
                    for x in sorted(uniform(start, end, pts_per_seg[seg]))
                ]
            ),
            dtype=float64,
        )

    return array([], dtype=float64)


def generate_temperatures(
    hours: NDArray[float64],
    base_temp: float = 18,
    amplitude: float = 7,
    period_hours: float = 24,
    noise_std: float = 1.2,
) -> NDArray[float64]:
    """Generate temperature values for given hours"""
    temps = base_temp + amplitude * sin(
        (hours * (24 / period_hours) - 6) * pi / 12
    )

    noise = normal(0, noise_std, hours.size)
    temps += noise

    return temps


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

    hours = generate_time_points(period_hours, num_points, interval_type)
    temps = generate_temperatures(
        hours, base_temp, amplitude, period_hours, noise_std
    )
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
