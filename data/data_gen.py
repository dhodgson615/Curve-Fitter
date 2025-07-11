import argparse

import numpy as np
import pandas as pd
from numpy import pi, sin
from numpy.random import normal, seed, uniform


class TemperatureDataGenerator:
    def __init__(
        self,
        period_hours=24,
        num_points=25,
        interval_type="regular",  # 'regular', 'random', 'weighted'
        base_temp=18,
        amplitude=7,
        noise_std=1.2,
        random_seed=None,
        output_file="data_points.csv",
    ):
        """Initialize temperature data generator with configurable
        parameters
        """
        self.period_hours = period_hours
        self.num_points = num_points
        self.interval_type = interval_type
        self.base_temp = base_temp
        self.amplitude = amplitude
        self.noise_std = noise_std
        self.output_file = output_file

        # Set random seed if provided
        if random_seed is not None:
            seed(random_seed)

    def generate_time_points(self):
        """Generate time points based on specified interval type"""
        if self.interval_type == "regular":
            # Regular intervals
            return np.linspace(0, self.period_hours, self.num_points)

        elif self.interval_type == "random":
            # Random intervals
            times = sorted(uniform(0, self.period_hours, self.num_points - 1))
            return np.append(times, self.period_hours)

        elif self.interval_type == "weighted":
            # More readings during day, fewer at night
            day_segments = {
                "early_morning": (0, 6),  # Fewer readings
                "morning": (6, 12),  # More readings
                "afternoon": (12, 18),  # More readings
                "night": (18, 24),  # Fewer readings
            }

            # Adjust segments if period is not 24 hours
            if self.period_hours != 24:
                scale = self.period_hours / 24
                day_segments = {
                    k: (v[0] * scale, v[1] * scale)
                    for k, v in day_segments.items()
                }

            # Assign points to segments based on weights
            weights = {
                "early_morning": 0.15,
                "morning": 0.3,
                "afternoon": 0.3,
                "night": 0.25,
            }

            points_per_segment = {
                seg: max(1, int(weights[seg] * self.num_points))
                for seg in day_segments
            }

            # Adjust if the sum doesn't match the required number of points
            total = sum(points_per_segment.values())
            diff = self.num_points - total

            if diff != 0:
                keys = list(points_per_segment.keys())
                for i in range(abs(diff)):
                    idx = i % len(keys)
                    points_per_segment[keys[idx]] += 1 if diff > 0 else -1

            # Generate points within each segment
            times = []
            for seg, (start, end) in day_segments.items():
                count = points_per_segment[seg]
                if count > 0:
                    segment_times = sorted(uniform(start, end, count))
                    times.extend(segment_times)

            return np.sort(times)

        else:
            raise ValueError(f"Unknown interval type: {self.interval_type}")

    def generate_temperatures(self, hours):
        """Generate temperature values for given hours"""
        # Scale the sine function to match the period
        scale_factor = 24 / self.period_hours
        temps = self.base_temp + self.amplitude * sin(
            (hours * scale_factor - 6) * pi / 12
        )

        # Add noise
        noise = normal(0, self.noise_std, len(hours))
        temps += noise

        return temps

    def generate_and_save(self):
        """Generate data and save to CSV file"""
        hours = self.generate_time_points()
        temps = self.generate_temperatures(hours)

        # Create DataFrame and save to CSV
        data = pd.DataFrame({"Time (hours)": hours, "Temperature (°C)": temps})
        data.to_csv(self.output_file, index=False)

        print(
            f"CSV file '{self.output_file}' created with {len(hours)} temperature data points across {self.period_hours} hours"
        )
        return data


def generate():
    """Parse command line arguments and generate data"""
    parser = argparse.ArgumentParser(
        description="Generate synthetic temperature data"
    )

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

    generator = TemperatureDataGenerator(
        period_hours=args.period,
        num_points=args.points,
        interval_type=args.intervals,
        base_temp=args.base_temp,
        amplitude=args.amplitude,
        noise_std=args.noise,
        random_seed=args.seed,
        output_file=args.output,
    )

    generator.generate_and_save()


if __name__ == "__main__":
    generate()
