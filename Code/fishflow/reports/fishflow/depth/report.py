"""
Depth report generation for FishFlow.

This module provides functions for building depth occupancy reports, including
geometry, timeline, cell depth, occupancy, and minimum probability data.
"""

import os
import json
import shutil
import pandas as pd
import numpy as np
import geojson
from typing import Dict, Any

from ..common.support import compute_support, compute_mixtures
from ..common.spacetime import build_geojson_h3, build_timeline


def build_cell_depths(context_df: pd.DataFrame) -> Dict[int, int]:
    """
    Get the deepest depth bin per cell_id.

    Args:
        context_df: DataFrame with at least columns ['cell_id', 'depth_bin'].

    Returns:
        Dictionary mapping cell_id to maximum depth_bin for that cell.

    Raises:
        ValueError: If required columns are missing.
    """
    required_cols = ['cell_id', 'depth_bin']
    if not all(col in context_df.columns for col in required_cols):
        raise ValueError(f"context_df must have columns {required_cols}")

    # Group by cell_id and get max depth_bin
    cell_depths = context_df.groupby('cell_id')['depth_bin'].max().to_dict()

    # Convert to int (in case they're numpy types)
    cell_depths = {int(k): int(v) for k, v in cell_depths.items()}

    return cell_depths


def build_occupancy(mixture_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build occupancy dataframe for a single cell.

    The output is structured so that columns represent combinations of depth bins
    and mixture models (epsilons), and rows are ordered by datetime.

    Args:
        mixture_df: DataFrame for a single cell_id with at least columns
            ['depth_bin', 'datetime', 'probability', 'epsilon'].

    Returns:
        DataFrame where:
        - Rows are datetimes (ordered earliest first)
        - Columns represent (epsilon, depth_bin) combinations
        - Column index calculation: col = model_idx * num_depth_bins + depth_bin_idx
          where model_idx is the index in sorted unique epsilons.

    Raises:
        ValueError: If required columns are missing.
    """
    required_cols = ['depth_bin', 'datetime', 'probability', 'epsilon']
    if not all(col in mixture_df.columns for col in required_cols):
        raise ValueError(f"mixture_df must have columns {required_cols}")

    # Get sorted unique values
    datetimes = sorted(mixture_df['datetime'].unique())
    epsilons = sorted(mixture_df['epsilon'].unique())
    depth_bins = sorted(mixture_df['depth_bin'].unique())

    num_depth_bins = len(depth_bins)
    num_models = len(epsilons)

    # Create mappings
    datetime_to_idx = {dt: i for i, dt in enumerate(datetimes)}
    epsilon_to_idx = {eps: i for i, eps in enumerate(epsilons)}
    depth_bin_to_idx = {db: i for i, db in enumerate(depth_bins)}

    # Initialize occupancy matrix
    n_rows = len(datetimes)
    n_cols = num_models * num_depth_bins
    occupancy = np.zeros((n_rows, n_cols))

    # Fill occupancy matrix
    for _, row in mixture_df.iterrows():
        row_idx = datetime_to_idx[row['datetime']]
        model_idx = epsilon_to_idx[row['epsilon']]
        depth_bin_idx = depth_bin_to_idx[row['depth_bin']]

        # Column calculation: col = model_idx * num_depth_bins + depth_bin_idx
        col_idx = model_idx * num_depth_bins + depth_bin_idx

        occupancy[row_idx, col_idx] = row['probability']

    # Convert to DataFrame
    occupancy_df = pd.DataFrame(occupancy)

    return occupancy_df


def build_minimums(
    mixture_df: pd.DataFrame,
    minimums: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Build minimums map for a mixture dataframe.

    Computes minimum probabilities for each combination of cell_id, depth_bin,
    month of year, and hour of day, using only epsilon=1 (non-reference model).

    Args:
        mixture_df: DataFrame with columns ['cell_id', 'depth_bin', 'datetime',
            'probability', 'epsilon'].
        minimums: Existing minimums dictionary to update. If None, creates new one.

    Returns:
        Updated minimums dictionary with structure:
        {cell_id: {depth_bin: {month: {hour: min_probability}}}}

    Raises:
        ValueError: If required columns are missing or datetime is not datetime type.
    """
    required_cols = ['cell_id', 'depth_bin', 'datetime', 'probability', 'epsilon']
    if not all(col in mixture_df.columns for col in required_cols):
        raise ValueError(f"mixture_df must have columns {required_cols}")

    if minimums is None:
        minimums = {}

    # Filter to epsilon = 1 (non-reference model)
    filtered = mixture_df[mixture_df['epsilon'] == 1.0].copy()

    if len(filtered) == 0:
        # No epsilon=1 data, return minimums unchanged
        return minimums

    # Extract month (0-11) and hour (0-23) from datetime
    # Convert to pandas datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(filtered['datetime']):
        filtered['datetime'] = pd.to_datetime(filtered['datetime'])

    filtered['month'] = filtered['datetime'].dt.month - 1  # Convert to 0-11
    filtered['hour'] = filtered['datetime'].dt.hour

    # Group by cell_id, depth_bin, month, hour and compute minimum probability
    grouped = filtered.groupby(
        ['cell_id', 'depth_bin', 'month', 'hour']
    )['probability'].min().reset_index()

    # Build nested dictionary structure
    for _, row in grouped.iterrows():
        cell_id = int(row['cell_id'])
        depth_bin = int(row['depth_bin'])
        month = int(row['month'])
        hour = int(row['hour'])
        min_prob = float(row['probability'])

        # Initialize nested structure as needed
        if cell_id not in minimums:
            minimums[cell_id] = {}
        if depth_bin not in minimums[cell_id]:
            minimums[cell_id][depth_bin] = {}
        if month not in minimums[cell_id][depth_bin]:
            minimums[cell_id][depth_bin][month] = {}

        minimums[cell_id][depth_bin][month][hour] = min_prob

    return minimums


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
    Build a complete depth report for FishFlow.

    This function creates a directory structure containing all the data files
    needed for a depth scenario report, including geometries, timeline, cell depths,
    minimums, support, and per-cell occupancy data.

    Args:
        meta_data: Metadata dictionary for this scenario (must include 'scenario_id').
        model_df: Model predictions with columns ['_decision', '_choice', 'probability'].
        reference_model_df: Reference model predictions with same structure as model_df.
        context_df: Context data with columns ['_decision', '_choice', 'datetime',
            'h3_index', 'depth_bin'].
        model_actuals_df: Model predictions on actuals data.
        reference_model_actuals_df: Reference model predictions on actuals data.
        selections_actuals_df: Actually observed choices with ['_decision', '_choice'].
        epsilons: Array of epsilon values (0 to 1) for mixture family.
        data_dir: Directory to create the scenario subdirectory in.

    Returns:
        None. Writes files to disk in the structure:
        {data_dir}/{scenario_id}/
            meta_data.json
            geometries.geojson
            cell_depths.json
            minimums.json
            timestamps.json
            support.json
            {cell_id}_occupancy.parquet.gz

    Raises:
        ValueError: If required data is missing or validation checks fail.
    """
    # Validate meta_data contains scenario_id
    if 'scenario_id' not in meta_data:
        raise ValueError("meta_data must contain 'scenario_id'")

    scenario_id = meta_data['scenario_id']

    # Data validation checks
    # Check that model_df and reference_model_df have the same decision-choice pairs
    model_pairs = set(zip(model_df['_decision'], model_df['_choice']))
    ref_pairs = set(zip(reference_model_df['_decision'], reference_model_df['_choice']))

    if model_pairs != ref_pairs:
        raise ValueError(
            "model_df and reference_model_df must have the same "
            "(_decision, _choice) pairs"
        )

    # Check actuals dataframes
    model_actuals_pairs = set(zip(model_actuals_df['_decision'], model_actuals_df['_choice']))
    ref_actuals_pairs = set(zip(reference_model_actuals_df['_decision'], reference_model_actuals_df['_choice']))

    if model_actuals_pairs != ref_actuals_pairs:
        raise ValueError(
            "model_actuals_df and reference_model_actuals_df must have the same "
            "(_decision, _choice) pairs"
        )

    # Check that selections_actuals_df decisions are in model_actuals_df
    selections_decisions = set(selections_actuals_df['_decision'])
    actuals_decisions = set(model_actuals_df['_decision'])

    if not selections_decisions.issubset(actuals_decisions):
        raise ValueError(
            "All decisions in selections_actuals_df must be in model_actuals_df"
        )

    # Check that all choices in selections_actuals_df are valid
    for _, row in selections_actuals_df.iterrows():
        decision = row['_decision']
        choice = row['_choice']
        if (decision, choice) not in model_actuals_pairs:
            raise ValueError(
                f"Selection ({decision}, {choice}) not found in model_actuals_df"
            )

    print(f"Building report for scenario {scenario_id}...")

    # Create scenario directory
    scenario_dir = os.path.join(data_dir, str(scenario_id))

    # If directory exists, remove it
    if os.path.exists(scenario_dir):
        shutil.rmtree(scenario_dir)

    os.makedirs(scenario_dir, exist_ok=True)

    # 1. Build geometries and get cell_id mapping
    print("Building geometries...")
    geojson_data, cell_id_df = build_geojson_h3(context_df)

    with open(os.path.join(scenario_dir, 'geometries.geojson'), 'w') as f:
        geojson.dump(geojson_data, f)

    # Add cell_id to context_df for subsequent operations
    context_df = context_df.merge(cell_id_df, on=['_decision', '_choice'], how='left')

    # 2. Build timeline
    print("Building timeline...")
    timeline = build_timeline(context_df)

    # Convert datetimes to ISO format strings for JSON serialization
    timeline_str = [str(dt) for dt in timeline]

    with open(os.path.join(scenario_dir, 'timestamps.json'), 'w') as f:
        json.dump(timeline_str, f)

    # 3. Build cell depths
    print("Building cell depths...")
    cell_depths = build_cell_depths(context_df)

    with open(os.path.join(scenario_dir, 'cell_depths.json'), 'w') as f:
        json.dump(cell_depths, f)

    # 4. Compute support
    print("Computing support...")
    support = compute_support(
        model_actuals_df,
        reference_model_actuals_df,
        selections_actuals_df,
        epsilons
    )

    # Convert to list for JSON serialization
    support_list = support.tolist()

    with open(os.path.join(scenario_dir, 'support.json'), 'w') as f:
        json.dump(support_list, f)

    # 5. Get unique cell_ids
    unique_cells = sorted(context_df['cell_id'].unique())

    print(f"Processing {len(unique_cells)} cells...")

    # 6. Initialize minimums
    minimums = {}

    # 7. Process each cell
    for cell_id in unique_cells:
        print(f"  Processing cell {cell_id}...")

        # Filter model_df and reference_model_df for this cell
        # First, get the decision-choice pairs for this cell
        cell_pairs = cell_id_df[cell_id_df['cell_id'] == cell_id][['_decision', '_choice']]

        cell_model_df = model_df.merge(cell_pairs, on=['_decision', '_choice'])
        cell_ref_df = reference_model_df.merge(cell_pairs, on=['_decision', '_choice'])

        # Compute mixtures for this cell
        cell_mixtures = compute_mixtures(cell_model_df, cell_ref_df, epsilons)

        # Add context (depth_bin, datetime, cell_id) from context_df
        cell_context = context_df[context_df['cell_id'] == cell_id][
            ['_decision', '_choice', 'depth_bin', 'datetime', 'cell_id']
        ]
        cell_mixtures = cell_mixtures.merge(
            cell_context,
            on=['_decision', '_choice'],
            how='left'
        )

        # Build occupancy for this cell
        occupancy_df = build_occupancy(cell_mixtures)

        # Save occupancy to parquet
        occupancy_path = os.path.join(scenario_dir, f'{cell_id}_occupancy.parquet.gz')
        occupancy_df.to_parquet(occupancy_path, compression='gzip', index=False)

        # Update minimums
        minimums = build_minimums(cell_mixtures, minimums)

    # 8. Save minimums
    print("Saving minimums...")

    # Convert all keys to strings for JSON
    minimums_str = {
        str(cell_id): {
            str(depth_bin): {
                str(month): {
                    str(hour): value
                    for hour, value in hours.items()
                }
                for month, hours in months.items()
            }
            for depth_bin, months in depth_bins.items()
        }
        for cell_id, depth_bins in minimums.items()
    }

    with open(os.path.join(scenario_dir, 'minimums.json'), 'w') as f:
        json.dump(minimums_str, f)

    # 9. Save meta_data
    print("Saving metadata...")
    with open(os.path.join(scenario_dir, 'meta_data.json'), 'w') as f:
        json.dump(meta_data, f)

    print(f"Report complete! Files written to {scenario_dir}")
