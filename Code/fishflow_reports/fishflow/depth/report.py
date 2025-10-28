"""
Depth occupancy report generation.

This module creates comprehensive depth occupancy reports by combining
model predictions with Bayesian model interpolation to quantify uncertainty.
"""

import os
import json
import shutil
import h3
import pandas as pd
import numpy as np
from typing import Dict, Any

from ..common.support import compute_support, compute_mixtures
from ..common.spacetime import build_geojson_h3, build_timeline


def build_minimums(
    mixture_df: pd.DataFrame,
    minimums: Dict[int, Dict[float, Dict[int, list]]] = None
) -> Dict[int, Dict[float, Dict[int, list]]]:
    """
    Compute minimum occupancy probabilities by cell, depth, month, and hour.

    For each spatial cell, depth bin, month of year, and hour of day,
    finds the minimum predicted occupancy probability from the complex
    model (epsilon=1).

    Args:
        mixture_df: DataFrame with columns 'cell_id', 'depth_bin', 'datetime',
            'probability', 'epsilon'.
        minimums: Optional existing minimums dict to update. If None, creates new.

    Returns:
        Nested dict structure:
        {cell_id -> {depth_bin -> {month -> [24 hourly minimums]}}}
        where month is 1-12 and the array has one minimum per hour (0-23).

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate input
    required_cols = {'cell_id', 'depth_bin', 'datetime', 'probability', 'epsilon'}
    if not required_cols.issubset(mixture_df.columns):
        raise ValueError(f"mixture_df must have columns {required_cols}")

    if minimums is None:
        minimums = {}

    # Filter to epsilon=1 (complex model only)
    filtered = mixture_df[mixture_df['epsilon'] == 1.0].copy()

    if len(filtered) == 0:
        return minimums

    # Extract month and hour from datetime
    filtered['month'] = pd.to_datetime(filtered['datetime']).dt.month  # 1-12
    filtered['hour'] = pd.to_datetime(filtered['datetime']).dt.hour  # 0-23

    # Group by cell_id, depth_bin, month, hour and find minimum
    grouped = filtered.groupby(['cell_id', 'depth_bin', 'month', 'hour'])['probability'].min()

    # Build nested dict structure
    for (cell_id, depth_bin, month, hour), min_prob in grouped.items():
        # Initialize nested dicts if needed
        if cell_id not in minimums:
            minimums[cell_id] = {}
        if depth_bin not in minimums[cell_id]:
            minimums[cell_id][depth_bin] = {}
        if month not in minimums[cell_id][depth_bin]:
            minimums[cell_id][depth_bin][month] = [np.inf] * 24

        # Update minimum for this hour
        current_min = minimums[cell_id][depth_bin][month][hour]
        minimums[cell_id][depth_bin][month][hour] = min(current_min, min_prob)

    # Convert np.inf back to a reasonable value (or keep as is for JSON serialization)
    # Actually, let's keep track of what we've seen and fill with actual minimums
    for cell_id in minimums:
        for depth_bin in minimums[cell_id]:
            for month in minimums[cell_id][depth_bin]:
                minimums[cell_id][depth_bin][month] = [
                    float(v) if v != np.inf else 0.0
                    for v in minimums[cell_id][depth_bin][month]
                ]

    return minimums


def build_occupancy(mixture_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build occupancy dataframe for a single cell.

    Creates a matrix where rows are timestamps (in order) and columns represent
    combinations of model (epsilon) and depth bin. Column layout:
    model_idx = col // num_depth_bins, depth_bin_idx = col % num_depth_bins

    Args:
        mixture_df: DataFrame for a single cell_id with columns 'depth_bin',
            'datetime', 'probability', 'epsilon'.

    Returns:
        DataFrame where:
        - Index is datetime (sorted)
        - Columns are integer indices (one per model-depth combination)
        - Values are occupancy probabilities

    Raises:
        ValueError: If required columns are missing or data is invalid.
    """
    # Validate input
    required_cols = {'depth_bin', 'datetime', 'probability', 'epsilon'}
    if not required_cols.issubset(mixture_df.columns):
        raise ValueError(f"mixture_df must have columns {required_cols}")

    # Get sorted unique values
    unique_datetimes = sorted(mixture_df['datetime'].unique())
    unique_epsilons = sorted(mixture_df['epsilon'].unique())
    unique_depth_bins = sorted(mixture_df['depth_bin'].unique())

    n_models = len(unique_epsilons)
    n_depth_bins = len(unique_depth_bins)
    n_times = len(unique_datetimes)

    # Create column count
    n_cols = n_models * n_depth_bins

    # Initialize output array
    occupancy_array = np.full((n_times, n_cols), np.nan)

    # Create index mappings
    datetime_to_idx = {dt: i for i, dt in enumerate(unique_datetimes)}
    epsilon_to_idx = {eps: i for i, eps in enumerate(unique_epsilons)}
    depth_bin_to_idx = {db: i for i, db in enumerate(unique_depth_bins)}

    # Fill array
    for _, row in mixture_df.iterrows():
        time_idx = datetime_to_idx[row['datetime']]
        model_idx = epsilon_to_idx[row['epsilon']]
        depth_idx = depth_bin_to_idx[row['depth_bin']]

        # Column follows the formula: model_idx * n_depth_bins + depth_idx
        col_idx = model_idx * n_depth_bins + depth_idx

        occupancy_array[time_idx, col_idx] = row['probability']

    # Create dataframe
    occupancy_df = pd.DataFrame(
        occupancy_array,
        index=unique_datetimes
    )

    return occupancy_df


def build_cell_depths(context_df: pd.DataFrame) -> Dict[int, float]:
    """
    Get maximum depth bin for each cell.

    Args:
        context_df: DataFrame with at least columns 'cell_id', 'depth_bin'.

    Returns:
        Dictionary mapping cell_id to maximum depth_bin value.

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate input
    required_cols = {'cell_id', 'depth_bin'}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(f"context_df must have columns {required_cols}")

    # Group by cell_id and get max depth_bin
    cell_depths = context_df.groupby('cell_id')['depth_bin'].max().to_dict()

    return cell_depths


def build_report(
    meta_data: Dict[str, Any],
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    context_df: pd.DataFrame,
    model_actuals_df: pd.DataFrame,
    reference_model_actuals_df: pd.DataFrame,
    selections_actuals_df: pd.DataFrame,
    epsilons: np.ndarray,
    data_dir: str
) -> None:
    """
    Build complete depth occupancy report.

    Creates a directory with all report files including metadata, geometries,
    timelines, and per-cell occupancy data.

    Args:
        meta_data: Dictionary with report metadata (see validation below).
        model_df: Model predictions with columns '_decision', '_choice', 'probability'.
        reference_model_df: Reference model predictions with same structure.
        context_df: Context data with '_decision', '_choice', 'datetime',
            'h3_index', 'depth_bin'.
        model_actuals_df: Model predictions on validation data.
        reference_model_actuals_df: Reference predictions on validation data.
        selections_actuals_df: Actual observed choices with '_decision', '_choice'.
        epsilons: Array of epsilon values for model mixture (0 to 1).
        data_dir: Directory where scenario subdirectory will be created.

    Raises:
        ValueError: If inputs are invalid or metadata is incomplete.
    """
    # Validate required metadata fields
    required_meta_fields = {
        'scenario_id', 'name', 'species', 'model', 'reference_model',
        'region', 'reference_region', 'description', 'reference_time_window',
        'zoom', 'center'
    }
    missing_fields = required_meta_fields - set(meta_data.keys())
    if missing_fields:
        raise ValueError(f"meta_data missing required fields: {missing_fields}")

    # Validate data consistency
    model_keys = set(zip(model_df['_decision'], model_df['_choice']))
    ref_keys = set(zip(reference_model_df['_decision'], reference_model_df['_choice']))
    if model_keys != ref_keys:
        raise ValueError("model_df and reference_model_df must have same (_decision, _choice) pairs")

    model_act_keys = set(zip(model_actuals_df['_decision'], model_actuals_df['_choice']))
    ref_act_keys = set(zip(reference_model_actuals_df['_decision'], reference_model_actuals_df['_choice']))
    if model_act_keys != ref_act_keys:
        raise ValueError("model_actuals_df and reference_model_actuals_df must have same pairs")

    # Get scenario_id
    scenario_id = meta_data['scenario_id']

    # Create output directory
    output_dir = os.path.join(data_dir, scenario_id)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Building report for scenario: {scenario_id}")

    # Compute support from actuals
    print("Computing model support...")
    support = compute_support(
        model_actuals_df,
        reference_model_actuals_df,
        selections_actuals_df,
        epsilons
    )

    # Build spatial geometries
    print("Building geometries...")
    geojson, cell_id_df = build_geojson_h3(context_df)

    # Save geometries
    with open(os.path.join(output_dir, 'geometries.geojson'), 'w') as f:
        json.dump(geojson, f)

    # Build timeline
    print("Building timeline...")
    timeline = build_timeline(context_df)

    # Save timeline (convert to ISO format strings)
    timeline_strings = [pd.Timestamp(dt).isoformat() for dt in timeline]
    with open(os.path.join(output_dir, 'timestamps.json'), 'w') as f:
        json.dump(timeline_strings, f)

    # Merge context with cell_ids
    context_with_cells = context_df.merge(cell_id_df, on=['_decision', '_choice'])

    # Build cell depths
    print("Building cell depths...")
    cell_depths = build_cell_depths(context_with_cells)

    # Save cell depths
    with open(os.path.join(output_dir, 'cell_depths.json'), 'w') as f:
        json.dump(cell_depths, f)

    # Get depth bins from context
    depth_bins = sorted(context_df['depth_bin'].unique())

    # Derive metadata from data
    print("Computing derived metadata...")

    # Get H3 resolution
    first_h3 = context_df['h3_index'].iloc[0]
    resolution = h3.get_resolution(first_h3)

    # Get time window
    all_datetimes = pd.to_datetime(context_df['datetime'])
    time_window = [
        all_datetimes.min().isoformat(),
        all_datetimes.max().isoformat()
    ]

    # Get grid size
    grid_size = len(geojson['features'])

    # Update metadata with derived values
    meta_data_complete = meta_data.copy()
    meta_data_complete.update({
        'resolution': resolution,
        'grid_size': grid_size,
        'depth_bins': [float(db) for db in depth_bins],
        'support': [float(s) for s in support],
        'time_window': time_window
    })

    # Save metadata
    with open(os.path.join(output_dir, 'meta_data.json'), 'w') as f:
        json.dump(meta_data_complete, f, indent=2)

    # Build mixtures and occupancy files per cell
    print("Building mixtures and occupancy files...")

    # Merge model data with context to get depth_bin, datetime, h3_index
    model_with_context = model_df.merge(
        context_df[['_decision', '_choice', 'datetime', 'h3_index', 'depth_bin']],
        on=['_decision', '_choice']
    )

    reference_with_context = reference_model_df.merge(
        context_df[['_decision', '_choice', 'datetime', 'h3_index', 'depth_bin']],
        on=['_decision', '_choice']
    )

    # Compute mixtures
    print("Computing model mixtures...")
    mixtures_df = compute_mixtures(model_with_context, reference_with_context, epsilons)

    # Add cell_id to mixtures
    mixtures_with_cells = mixtures_df.merge(cell_id_df, on=['_decision', '_choice'])

    # Initialize minimums dict
    minimums = {}

    # Get unique cell_ids
    unique_cells = sorted(mixtures_with_cells['cell_id'].unique())

    print(f"Processing {len(unique_cells)} cells...")

    for cell_id in unique_cells:
        # Filter to this cell
        cell_mixture = mixtures_with_cells[mixtures_with_cells['cell_id'] == cell_id].copy()

        # Build occupancy dataframe
        occupancy_df = build_occupancy(cell_mixture)

        # Save as compressed parquet
        occupancy_file = os.path.join(output_dir, f'{cell_id}_occupancy.parquet.gz')
        occupancy_df.to_parquet(occupancy_file, compression='gzip')

        # Update minimums
        minimums = build_minimums(cell_mixture, minimums)

        if (cell_id + 1) % 10 == 0:
            print(f"  Processed {cell_id + 1}/{len(unique_cells)} cells")

    # Save minimums
    print("Saving minimums...")
    # Convert all keys to strings for JSON serialization
    minimums_serializable = {
        str(cell_id): {
            str(depth_bin): {
                str(month): hours
                for month, hours in month_dict.items()
            }
            for depth_bin, month_dict in depth_dict.items()
        }
        for cell_id, depth_dict in minimums.items()
    }

    with open(os.path.join(output_dir, 'minimums.json'), 'w') as f:
        json.dump(minimums_serializable, f)

    print(f"Report complete! Saved to {output_dir}")
