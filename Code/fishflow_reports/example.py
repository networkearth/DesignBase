#!/usr/bin/env python3
"""
Example script demonstrating FishFlow Reports usage.

This creates a complete synthetic depth occupancy report for demonstration purposes.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import h3

from fishflow.depth.report import build_report


def generate_synthetic_data():
    """Generate synthetic fish depth occupancy data for testing."""

    print("Generating synthetic data...")

    # Define spatial grid (H3 hexagons in Gulf of Mexico region)
    center_lat, center_lon = 27.0, -88.0
    resolution = 5

    # Get central H3 index and its neighbors
    center_h3 = h3.latlng_to_cell(center_lat, center_lon, resolution)
    h3_indices = [center_h3] + h3.grid_disk(center_h3, 1)
    h3_indices = list(h3_indices)[:5]  # Use 5 cells for demo

    print(f"  Using {len(h3_indices)} spatial cells")

    # Define temporal grid (48 hours, hourly)
    start_time = datetime(2023, 6, 1, 0, 0, 0)
    timestamps = [start_time + timedelta(hours=i) for i in range(48)]

    print(f"  Using {len(timestamps)} timestamps")

    # Define depth bins (meters)
    depth_bins = [10.0, 20.0, 30.0, 40.0, 50.0]

    print(f"  Using {len(depth_bins)} depth bins: {depth_bins}")

    # Generate decisions and choices
    decision_id = 0
    rows = []

    for timestamp in timestamps:
        for h3_idx in h3_indices:
            # Create one decision per (time, location)
            for depth in depth_bins:
                rows.append(
                    {
                        "_decision": decision_id,
                        "_choice": f"depth_{depth}_loc_{h3_idx[:6]}",
                        "datetime": timestamp,
                        "h3_index": h3_idx,
                        "depth_bin": depth,
                    }
                )
            decision_id += 1

    context_df = pd.DataFrame(rows)

    print(f"  Generated {len(context_df)} choice-contexts ({decision_id} decisions)")

    # Generate model predictions (complex model with depth-time patterns)
    model_rows = []
    for decision in context_df["_decision"].unique():
        decision_data = context_df[context_df["_decision"] == decision]

        # Parse timestamp to get hour of day
        dt = pd.to_datetime(decision_data.iloc[0]["datetime"])
        hour = dt.hour

        # Simulate depth preference: deeper during day, shallower at night
        # Peak at noon (hour 12), minimum at midnight (hour 0)
        time_factor = np.cos((hour - 12) * 2 * np.pi / 24)

        # Generate probabilities that favor deeper water during day
        depths = decision_data["depth_bin"].values

        # Deeper preference when time_factor is positive (daytime)
        if time_factor > 0:
            # Favor deeper bins
            logits = depths / 20.0 + np.random.normal(0, 0.5, len(depths))
        else:
            # Favor shallower bins
            logits = -depths / 20.0 + np.random.normal(0, 0.5, len(depths))

        # Convert to probabilities
        probs = np.exp(logits)
        probs = probs / probs.sum()

        for choice, prob in zip(decision_data["_choice"], probs):
            model_rows.append(
                {"_decision": decision, "_choice": choice, "probability": prob}
            )

    model_df = pd.DataFrame(model_rows)

    # Generate reference model (uniform across depth bins)
    reference_rows = []
    for decision in context_df["_decision"].unique():
        choices = context_df[context_df["_decision"] == decision]["_choice"]
        n_choices = len(choices)
        uniform_prob = 1.0 / n_choices

        for choice in choices:
            reference_rows.append(
                {"_decision": decision, "_choice": choice, "probability": uniform_prob}
            )

    reference_df = pd.DataFrame(reference_rows)

    # Generate validation data (subset of decisions with observations)
    n_validation = 50
    validation_decisions = np.random.choice(
        context_df["_decision"].unique(), size=n_validation, replace=False
    )

    # Model actuals (predictions on validation set)
    model_actuals_df = model_df[model_df["_decision"].isin(validation_decisions)].copy()
    reference_actuals_df = reference_df[
        reference_df["_decision"].isin(validation_decisions)
    ].copy()

    # Selections (simulated observations)
    # Sample from model predictions to create realistic selections
    selections = []
    for decision in validation_decisions:
        decision_model = model_actuals_df[model_actuals_df["_decision"] == decision]

        # Sample choice based on model probabilities
        selected_choice = np.random.choice(
            decision_model["_choice"].values, p=decision_model["probability"].values
        )

        selections.append({"_decision": decision, "_choice": selected_choice})

    selections_df = pd.DataFrame(selections)

    print(
        f"  Generated {len(validation_decisions)} validation decisions with observations"
    )

    return (
        context_df,
        model_df,
        reference_df,
        model_actuals_df,
        reference_actuals_df,
        selections_df,
    )


def main():
    """Run example report generation."""

    print("\n" + "=" * 70)
    print("FishFlow Reports - Example Report Generation")
    print("=" * 70 + "\n")

    # Generate synthetic data
    (
        context_df,
        model_df,
        reference_df,
        model_actuals_df,
        reference_actuals_df,
        selections_df,
    ) = generate_synthetic_data()

    # Define metadata
    meta_data = {
        "scenario_id": "example",
        "name": "Example Bluefin Tuna Depth Analysis",
        "species": "Bluefin Tuna (Thunnus thynnus)",
        "model": "Time-Varying Environmental Response Model",
        "reference_model": "Uniform Depth Distribution",
        "region": "Gulf of Mexico",
        "reference_region": "Historical Data 2020-2022",
        "description": "Synthetic example showing depth occupancy with diurnal patterns",
        "reference_time_window": ["2020-01-01 00:00:00", "2022-12-31 23:59:59"],
        "zoom": 6,
        "center": [-88.0, 27.0],
    }

    # Define mixture family (21 models from pure reference to pure complex)
    epsilons = np.linspace(0, 1, 21)

    print("\nBuilding report...")
    print(f"  Scenario ID: {meta_data['scenario_id']}")
    print(f"  Epsilon values: {len(epsilons)} (from 0.0 to 1.0)")

    # Build report
    build_report(
        meta_data=meta_data,
        model_df=model_df,
        reference_model_df=reference_df,
        context_df=context_df,
        model_actuals_df=model_actuals_df,
        reference_model_actuals_df=reference_actuals_df,
        selections_actuals_df=selections_df,
        epsilons=epsilons,
        data_dir="./depth",
    )

    print("\n" + "=" * 70)
    print("Report generation complete!")
    print("=" * 70)
    print("\nOutput location: ./example_output/example_bluefin_2023/")
    print("\nGenerated files:")
    print("  - meta_data.json          (scenario metadata)")
    print("  - geometries.geojson      (H3 hexagon geometries)")
    print("  - cell_depths.json        (maximum depth per cell)")
    print("  - minimums.json           (minimum occupancy stats)")
    print("  - timestamps.json         (timeline)")
    print("  - *_occupancy.parquet.gz  (occupancy time series per cell)")
    print("\nYou can now load this report in the FishFlow app for visualization.")
    print()


if __name__ == "__main__":
    main()
