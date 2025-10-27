"""
Depth report generation for FishFlow.

This module provides functions for building complete depth distribution reports
using Bayesian model interpolation.
"""

import os
import json
import shutil
import pandas as pd
import numpy as np
import h3
from typing import Dict, Any
from datetime import datetime

from fishflow.common.support import compute_support, compute_mixtures
from fishflow.common.spacetime import build_geojson_h3, build_timeline


def build_cell_depths(context_df: pd.DataFrame) -> Dict[int, float]:
    """
    Get the maximum depth bin for each cell ID.

    Args:
        context_df: DataFrame with at least columns ['cell_id', 'depth_bin'].

    Returns:
        Dictionary mapping cell_id to maximum depth_bin value for that cell.

    Raises:
        ValueError: If required columns are missing.
    """
    required_cols = {"cell_id", "depth_bin"}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(
            f"context_df must contain columns: {required_cols}, "
            f"but has: {context_df.columns.tolist()}"
        )

    # Group by cell_id and get maximum depth_bin
    cell_depths = context_df.groupby("cell_id")["depth_bin"].max().to_dict()

    return cell_depths


def build_minimums(
    mixture_df: pd.DataFrame, minimums: Dict[int, Dict[float, Dict[int, list]]] = None
) -> Dict[int, Dict[float, Dict[int, list]]]:
    """
    Create minimums map showing minimum occupancy per cell, depth, month, and hour.

    Args:
        mixture_df: DataFrame with columns ['cell_id', 'depth_bin', 'datetime',
            'probability', 'epsilon'].
        minimums: Existing minimums dictionary to update. Defaults to empty dict.

    Returns:
        Dictionary with structure:
        {cell_id(int) -> {depth_bin(float) -> {month(int) -> minimums_array}}}
        where minimums_array is length 24 containing minimum probabilities per hour.

    Raises:
        ValueError: If required columns are missing.
    """
    if minimums is None:
        minimums = {}

    required_cols = {"cell_id", "depth_bin", "datetime", "probability", "epsilon"}
    if not required_cols.issubset(mixture_df.columns):
        raise ValueError(
            f"mixture_df must contain columns: {required_cols}, "
            f"but has: {mixture_df.columns.tolist()}"
        )

    # Filter to epsilon = 1 (non-reference model)
    filtered = mixture_df[mixture_df["epsilon"] == 1.0].copy()

    if len(filtered) == 0:
        return minimums

    # Extract month and hour from datetime
    filtered["month"] = pd.to_datetime(filtered["datetime"]).dt.month
    filtered["hour"] = pd.to_datetime(filtered["datetime"]).dt.hour

    # Group by cell_id, depth_bin, month, hour and take minimum probability
    grouped = (
        filtered.groupby(["cell_id", "depth_bin", "month", "hour"])["probability"]
        .min()
        .reset_index()
    )

    # Build nested dictionary structure
    for _, row in grouped.iterrows():
        cell_id = int(row["cell_id"])
        depth_bin = float(row["depth_bin"])
        month = int(row["month"])
        hour = int(row["hour"])
        prob = float(row["probability"])

        # Initialize nested structure if needed
        if cell_id not in minimums:
            minimums[cell_id] = {}
        if depth_bin not in minimums[cell_id]:
            minimums[cell_id][depth_bin] = {}
        if month not in minimums[cell_id][depth_bin]:
            # Initialize array of 24 hours with None
            minimums[cell_id][depth_bin][month] = [None] * 24

        # Update minimum for this hour
        if minimums[cell_id][depth_bin][month][hour] is None:
            minimums[cell_id][depth_bin][month][hour] = prob
        else:
            minimums[cell_id][depth_bin][month][hour] = min(
                minimums[cell_id][depth_bin][month][hour], prob
            )

    return minimums


def build_occupancy(mixture_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build occupancy dataframe for a single cell.

    Creates a pivot table where rows are timestamps and columns represent
    combinations of depth bins and mixture models (epsilon values).

    Args:
        mixture_df: DataFrame for a single cell_id with columns ['depth_bin',
            'datetime', 'probability', 'epsilon'].

    Returns:
        DataFrame where:
        - Rows are sorted datetime values
        - Columns represent depth_bin x epsilon combinations
        - Column index formula: model_idx = col // num_depth_bins,
          depth_bin_idx = col % num_depth_bins
        - Values are probabilities

    Raises:
        ValueError: If required columns are missing.
    """
    required_cols = {"depth_bin", "datetime", "probability", "epsilon"}
    if not required_cols.issubset(mixture_df.columns):
        raise ValueError(
            f"mixture_df must contain columns: {required_cols}, "
            f"but has: {mixture_df.columns.tolist()}"
        )

    # Get sorted unique values
    sorted_datetimes = sorted(mixture_df["datetime"].unique())
    sorted_epsilons = sorted(mixture_df["epsilon"].unique())
    sorted_depth_bins = sorted(mixture_df["depth_bin"].unique())

    num_depth_bins = len(sorted_depth_bins)
    num_models = len(sorted_epsilons)

    # Create column index: for each model, then for each depth bin
    # This ensures model_idx = col // num_depth_bins
    columns = []
    for model_idx in range(num_models):
        for depth_bin_idx in range(num_depth_bins):
            columns.append((sorted_epsilons[model_idx], sorted_depth_bins[depth_bin_idx]))

    # Initialize result dataframe
    occupancy_df = pd.DataFrame(
        index=range(len(sorted_datetimes)), columns=range(len(columns)), dtype=float
    )

    # Fill in values
    for dt_idx, dt in enumerate(sorted_datetimes):
        for col_idx, (epsilon, depth_bin) in enumerate(columns):
            # Find matching row in mixture_df
            matches = mixture_df[
                (mixture_df["datetime"] == dt)
                & (mixture_df["epsilon"] == epsilon)
                & (mixture_df["depth_bin"] == depth_bin)
            ]

            if len(matches) > 0:
                occupancy_df.iloc[dt_idx, col_idx] = matches.iloc[0]["probability"]

    return occupancy_df


def build_report(
    meta_data: Dict[str, Any],
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    context_df: pd.DataFrame,
    model_actuals_df: pd.DataFrame,
    reference_model_actuals_df: pd.DataFrame,
    selections_actuals_df: pd.DataFrame,
    epsilons: np.ndarray,
    data_dir: str,
) -> None:
    """
    Build complete depth distribution report.

    Creates a directory structure with all necessary files for a FishFlow depth report,
    including metadata, geometries, timelines, and occupancy data.

    Args:
        meta_data: Dictionary with required keys:
            - scenario_id: str
            - name: str
            - species: str
            - model: str
            - reference_model: str
            - region: str
            - reference_region: str
            - description: str
            - reference_time_window: [datetime, datetime]
            - zoom: int (zoom for a map)
            - center: (lon, lat) (center for a map)
        model_df: DataFrame with ['_decision', '_choice', 'probability'] for hypothesis model.
        reference_model_df: DataFrame with ['_decision', '_choice', 'probability']
            for reference model.
        context_df: DataFrame with ['_decision', '_choice', 'datetime', 'h3_index', 'depth_bin'].
        model_actuals_df: DataFrame with ['_decision', '_choice', 'probability'] for
            hypothesis model on actual data.
        reference_model_actuals_df: DataFrame with ['_decision', '_choice', 'probability']
            for reference model on actual data.
        selections_actuals_df: DataFrame with ['_decision', '_choice'] of observed choices.
        epsilons: Array of floats from 0 to 1 defining mixture family density.
        data_dir: Directory to create the {scenario_id} subdirectory in.

    Raises:
        ValueError: If required metadata fields are missing or data checks fail.
    """
    # Validate required metadata fields
    required_meta_fields = {
        "scenario_id",
        "name",
        "species",
        "model",
        "reference_model",
        "region",
        "reference_region",
        "description",
        "reference_time_window",
        "zoom",
        "center",
    }

    missing_fields = required_meta_fields - set(meta_data.keys())
    if missing_fields:
        raise ValueError(f"meta_data is missing required fields: {missing_fields}")

    scenario_id = meta_data["scenario_id"]

    # Data validation checks
    # Check that model_df and reference_model_df have same decision-choice pairs
    model_keys = set(
        zip(model_df["_decision"].values, model_df["_choice"].values)
    )
    ref_keys = set(
        zip(
            reference_model_df["_decision"].values,
            reference_model_df["_choice"].values,
        )
    )
    if model_keys != ref_keys:
        raise ValueError(
            "model_df and reference_model_df must have identical _decision and _choice pairs"
        )

    # Check actuals dataframes
    model_actuals_keys = set(
        zip(
            model_actuals_df["_decision"].values,
            model_actuals_df["_choice"].values,
        )
    )
    ref_actuals_keys = set(
        zip(
            reference_model_actuals_df["_decision"].values,
            reference_model_actuals_df["_choice"].values,
        )
    )
    if model_actuals_keys != ref_actuals_keys:
        raise ValueError(
            "model_actuals_df and reference_model_actuals_df must have "
            "identical _decision and _choice pairs"
        )

    # Check that selections have valid decisions and choices
    selection_decisions = set(selections_actuals_df["_decision"].values)
    actuals_decisions = set(model_actuals_df["_decision"].values)
    if not selection_decisions.issubset(actuals_decisions):
        raise ValueError(
            "selections_actuals_df contains decisions not in model_actuals_df"
        )

    # Create scenario directory (overwrite if exists)
    scenario_dir = os.path.join(data_dir, scenario_id)
    if os.path.exists(scenario_dir):
        shutil.rmtree(scenario_dir)
    os.makedirs(scenario_dir)

    print(f"Building report in {scenario_dir}")

    # Build GeoJSON and cell IDs
    print("Building geometries...")
    geojson, cell_ids_df = build_geojson_h3(context_df)

    # Merge cell_ids back into context_df
    context_with_cells = context_df.merge(cell_ids_df, on=["_decision", "_choice"])

    # Save geometries
    with open(os.path.join(scenario_dir, "geometries.geojson"), "w") as f:
        json.dump(geojson, f)

    # Build timeline
    print("Building timeline...")
    timeline = build_timeline(context_df)

    # Convert timeline to strings for JSON serialization
    timeline_str = [
        dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, "strftime") else str(dt)
        for dt in timeline
    ]

    with open(os.path.join(scenario_dir, "timestamps.json"), "w") as f:
        json.dump(timeline_str, f)

    # Build cell depths
    print("Building cell depths...")
    cell_depths = build_cell_depths(context_with_cells)

    with open(os.path.join(scenario_dir, "cell_depths.json"), "w") as f:
        json.dump(cell_depths, f)

    # Compute support
    print("Computing support...")
    support = compute_support(
        model_actuals_df,
        reference_model_actuals_df,
        selections_actuals_df,
        epsilons,
    )

    # Derive additional metadata from data
    # Get H3 resolution from first h3_index
    first_h3 = context_df["h3_index"].iloc[0]
    resolution = h3.get_resolution(first_h3)

    grid_size = len(geojson["features"])

    # Get depth bins from context
    depth_bins = sorted(context_df["depth_bin"].unique())

    # Get time window from context
    min_time = context_df["datetime"].min()
    max_time = context_df["datetime"].max()

    # Format time window
    time_window = [
        min_time.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(min_time, "strftime")
        else str(min_time),
        max_time.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(max_time, "strftime")
        else str(max_time),
    ]

    # Build complete metadata
    complete_meta_data = {
        **meta_data,
        "resolution": resolution,
        "grid_size": grid_size,
        "depth_bins": depth_bins,
        "support": support.tolist(),
        "time_window": time_window,
    }

    # Save metadata
    with open(os.path.join(scenario_dir, "meta_data.json"), "w") as f:
        json.dump(complete_meta_data, f, indent=2)

    # Get unique cell IDs
    unique_cell_ids = sorted(context_with_cells["cell_id"].unique())

    # Initialize minimums
    minimums = {}

    # Process each cell
    print(f"Processing {len(unique_cell_ids)} cells...")
    for cell_id in unique_cell_ids:
        print(f"  Processing cell {cell_id}...")

        # Filter context to this cell
        cell_context = context_with_cells[context_with_cells["cell_id"] == cell_id]

        # Get decisions and choices for this cell
        cell_decisions_choices = cell_context[["_decision", "_choice"]]

        # Filter model data to this cell
        cell_model_df = model_df.merge(cell_decisions_choices, on=["_decision", "_choice"])
        cell_ref_df = reference_model_df.merge(
            cell_decisions_choices, on=["_decision", "_choice"]
        )

        # Compute mixtures for this cell
        mixtures_df = compute_mixtures(cell_model_df, cell_ref_df, epsilons)

        # Merge in context (datetime, depth_bin)
        mixtures_with_context = mixtures_df.merge(
            context_with_cells[["_decision", "_choice", "datetime", "depth_bin", "cell_id"]],
            on=["_decision", "_choice"],
        )

        # Build minimums for this cell
        minimums = build_minimums(mixtures_with_context, minimums)

        # Build occupancy for this cell
        occupancy_df = build_occupancy(mixtures_with_context)

        # Save occupancy as compressed parquet
        occupancy_file = os.path.join(scenario_dir, f"{cell_id}_occupancy.parquet.gz")
        occupancy_df.to_parquet(occupancy_file, compression="gzip", index=False)

    # Save minimums
    print("Saving minimums...")
    # Convert minimums to JSON-serializable format
    minimums_serializable = {
        str(cell_id): {
            str(depth_bin): {
                str(month): [float(v) if v is not None else None for v in hours]
                for month, hours in months.items()
            }
            for depth_bin, months in depths.items()
        }
        for cell_id, depths in minimums.items()
    }

    with open(os.path.join(scenario_dir, "minimums.json"), "w") as f:
        json.dump(minimums_serializable, f)

    print(f"Report build complete: {scenario_dir}")
