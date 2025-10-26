"""
Depth report building functions for FishFlow.

This module provides functions to build depth occupancy reports that can be
consumed by the FishFlow API and viewed in the FishFlow app.
"""

import os
import json
import shutil
import pandas as pd
import numpy as np
from typing import Dict, Any

from ..common.support import compute_support, compute_mixtures
from ..common.spacetime import build_geojson_h3, build_timeline


def build_cell_depths(context_df: pd.DataFrame) -> Dict[int, int]:
    """
    Get the deepest depth bin per cell_id.

    Args:
        context_df: DataFrame with at least columns 'cell_id' and 'depth_bin'.

    Returns:
        Dictionary mapping cell_id to the maximum depth_bin value for that cell.

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate required columns
    required_cols = {'cell_id', 'depth_bin'}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(f"context_df must have columns: {required_cols}")

    # Group by cell_id and find max depth_bin
    cell_depths = context_df.groupby('cell_id')['depth_bin'].max().to_dict()

    # Convert keys and values to int for JSON serialization
    cell_depths = {int(k): int(v) for k, v in cell_depths.items()}

    return cell_depths


def build_occupancy(mixture_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build an occupancy dataframe for a single cell_id.

    The resulting dataframe has datetime as rows (sorted earliest first) and
    combinations of (depth_bin, epsilon) as columns. Column index calculation:
    - model_idx = col // num_depth_bins
    - depth_bin_idx = col % num_depth_bins

    Args:
        mixture_df: DataFrame with columns 'depth_bin', 'datetime', 'probability',
            'epsilon' for a single cell_id.

    Returns:
        DataFrame where:
            - Rows are sorted datetimes
            - Columns represent (depth_bin, epsilon) combinations
            - Values are probabilities

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate required columns
    required_cols = {'depth_bin', 'datetime', 'probability', 'epsilon'}
    if not required_cols.issubset(mixture_df.columns):
        raise ValueError(f"mixture_df must have columns: {required_cols}")

    if len(mixture_df) == 0:
        raise ValueError("mixture_df must not be empty")

    # Get sorted unique values
    unique_datetimes = sorted(mixture_df['datetime'].unique())
    unique_depth_bins = sorted(mixture_df['depth_bin'].unique())
    unique_epsilons = sorted(mixture_df['epsilon'].unique())

    num_depth_bins = len(unique_depth_bins)
    num_models = len(unique_epsilons)

    # Create mappings
    datetime_to_row = {dt: i for i, dt in enumerate(unique_datetimes)}
    depth_bin_to_idx = {db: i for i, db in enumerate(unique_depth_bins)}
    epsilon_to_model_idx = {eps: i for i, eps in enumerate(unique_epsilons)}

    # Initialize output matrix
    n_rows = len(unique_datetimes)
    n_cols = num_models * num_depth_bins
    occupancy_matrix = np.zeros((n_rows, n_cols))

    # Fill the matrix
    for _, row in mixture_df.iterrows():
        row_idx = datetime_to_row[row['datetime']]
        depth_bin_idx = depth_bin_to_idx[row['depth_bin']]
        model_idx = epsilon_to_model_idx[row['epsilon']]

        # Column calculation: model_idx * num_depth_bins + depth_bin_idx
        col_idx = model_idx * num_depth_bins + depth_bin_idx

        occupancy_matrix[row_idx, col_idx] = row['probability']

    # Create dataframe with datetime index
    occupancy_df = pd.DataFrame(
        occupancy_matrix,
        index=unique_datetimes
    )

    return occupancy_df


def build_minimums(mixture_df: pd.DataFrame, minimums: Dict = None) -> Dict:
    """
    Build or update a minimums map from mixture data.

    The minimums map structure (per design):
    {
        cell_id: {
            depth_bin: {
                month: minimums_array  # Array of 24 elements (hours 0-23)
            }
        }
    }

    Args:
        mixture_df: DataFrame with columns 'cell_id', 'depth_bin', 'datetime',
            'probability', 'epsilon'.
        minimums: Optional existing minimums dictionary to update. If None,
            creates a new one.

    Returns:
        Updated minimums dictionary where minimums_array is an array of length 24
        representing the minimums per hour (from 0-23).

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate required columns
    required_cols = {'cell_id', 'depth_bin', 'datetime', 'probability', 'epsilon'}
    if not required_cols.issubset(mixture_df.columns):
        raise ValueError(f"mixture_df must have columns: {required_cols}")

    if minimums is None:
        minimums = {}

    # Filter to epsilon = 1 (non-reference model)
    filtered = mixture_df[mixture_df['epsilon'] == 1.0].copy()

    if len(filtered) == 0:
        return minimums

    # Convert datetime to pandas datetime if not already
    filtered['datetime'] = pd.to_datetime(filtered['datetime'])

    # Extract month (0-11) and hour (0-23)
    filtered['month'] = filtered['datetime'].dt.month - 1  # Convert 1-12 to 0-11
    filtered['hour'] = filtered['datetime'].dt.hour

    # Group by cell_id, depth_bin, month, hour and take minimum probability
    grouped = filtered.groupby(['cell_id', 'depth_bin', 'month', 'hour'])['probability'].min()

    # Build the nested dictionary structure with arrays for hours
    for (cell_id, depth_bin, month, hour), min_prob in grouped.items():
        cell_id = int(cell_id)
        depth_bin = int(depth_bin)
        month = int(month)
        hour = int(hour)

        if cell_id not in minimums:
            minimums[cell_id] = {}
        if depth_bin not in minimums[cell_id]:
            minimums[cell_id][depth_bin] = {}
        if month not in minimums[cell_id][depth_bin]:
            # Initialize array of 24 hours with None or infinity
            minimums[cell_id][depth_bin][month] = [float('inf')] * 24

        # Update the specific hour in the array
        minimums[cell_id][depth_bin][month][hour] = float(min_prob)

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
    Build a complete depth occupancy report.

    This function creates a directory structure containing:
    - meta_data.json
    - geometries.geojson
    - cell_depths.json
    - minimums.json
    - timestamps.json
    - {cell_id}_occupancy.parquet.gz (one per cell)

    Args:
        meta_data: Metadata dictionary for this scenario (must include 'scenario_id').
        model_df: DataFrame with '_decision', '_choice', 'probability' for the target model.
        reference_model_df: DataFrame with '_decision', '_choice', 'probability' for
            the reference model.
        context_df: DataFrame with '_decision', '_choice', 'datetime', 'h3_index', 'depth_bin'
            providing context for each choice.
        model_actuals_df: DataFrame with '_decision', '_choice', 'probability' for the
            target model on actual data.
        reference_model_actuals_df: DataFrame with '_decision', '_choice', 'probability' for
            the reference model on actual data.
        selections_actuals_df: DataFrame with '_decision', '_choice' for actually observed
            selections (one choice per decision).
        epsilons: Array of mixing parameters (0 to 1) defining the model family.
        data_dir: Directory to create the scenario directory in.

    Raises:
        ValueError: If inputs are invalid or have mismatched decision/choice pairs.
    """
    # Validate that scenario_id is in meta_data
    if 'scenario_id' not in meta_data:
        raise ValueError("meta_data must contain 'scenario_id'")

    scenario_id = meta_data['scenario_id']

    # Data validation: model_df and reference_model_df should have same decision/choice pairs
    model_pairs = set(zip(model_df['_decision'], model_df['_choice']))
    ref_pairs = set(zip(reference_model_df['_decision'], reference_model_df['_choice']))

    if model_pairs != ref_pairs:
        raise ValueError(
            "model_df and reference_model_df must have the same (_decision, _choice) pairs"
        )

    # Validate actuals dataframes
    model_actuals_pairs = set(zip(model_actuals_df['_decision'], model_actuals_df['_choice']))
    ref_actuals_pairs = set(zip(reference_model_actuals_df['_decision'], reference_model_actuals_df['_choice']))

    if model_actuals_pairs != ref_actuals_pairs:
        raise ValueError(
            "model_actuals_df and reference_model_actuals_df must have the same "
            "(_decision, _choice) pairs"
        )

    # Check that selections_actuals_df decisions match model_actuals_df decisions
    selections_decisions = set(selections_actuals_df['_decision'])
    actuals_decisions = set(model_actuals_df['_decision'])

    if not selections_decisions.issubset(actuals_decisions):
        raise ValueError(
            "All decisions in selections_actuals_df must exist in model_actuals_df"
        )

    # Create scenario directory (overwrite if exists)
    scenario_dir = os.path.join(data_dir, str(scenario_id))

    if os.path.exists(scenario_dir):
        shutil.rmtree(scenario_dir)

    os.makedirs(scenario_dir, exist_ok=True)

    print(f"Building report for scenario {scenario_id}...")

    # 1. Write meta_data.json
    meta_data_path = os.path.join(scenario_dir, 'meta_data.json')
    with open(meta_data_path, 'w') as f:
        json.dump(meta_data, f, indent=2)
    print(f"  ✓ Wrote meta_data.json")

    # 2. Build and write geometries.geojson
    geojson, cell_id_df = build_geojson_h3(context_df)
    geojson_path = os.path.join(scenario_dir, 'geometries.geojson')
    with open(geojson_path, 'w') as f:
        json.dump(geojson, f, indent=2)
    print(f"  ✓ Wrote geometries.geojson ({len(geojson['features'])} cells)")

    # 3. Merge cell_id into context_df
    context_with_cells = pd.merge(
        context_df,
        cell_id_df,
        on=['_decision', '_choice'],
        how='left'
    )

    # 4. Build and write cell_depths.json
    cell_depths = build_cell_depths(context_with_cells)
    cell_depths_path = os.path.join(scenario_dir, 'cell_depths.json')
    with open(cell_depths_path, 'w') as f:
        json.dump(cell_depths, f, indent=2)
    print(f"  ✓ Wrote cell_depths.json")

    # 5. Build and write timestamps.json
    timeline = build_timeline(context_df)
    timestamps_path = os.path.join(scenario_dir, 'timestamps.json')
    with open(timestamps_path, 'w') as f:
        json.dump(timeline, f, indent=2)
    print(f"  ✓ Wrote timestamps.json ({len(timeline)} timestamps)")

    # 6. Compute support
    support = compute_support(
        model_actuals_df,
        reference_model_actuals_df,
        selections_actuals_df,
        epsilons
    )
    support_path = os.path.join(scenario_dir, 'support.json')
    with open(support_path, 'w') as f:
        json.dump(support.tolist(), f, indent=2)
    print(f"  ✓ Computed and wrote support.json")

    # 7. Get unique cell_ids
    unique_cell_ids = sorted(context_with_cells['cell_id'].unique())

    # 8. Initialize minimums
    minimums = {}

    # 9. Build mixtures and occupancy files one cell at a time
    print(f"  Building occupancy files for {len(unique_cell_ids)} cells...")

    for cell_id in unique_cell_ids:
        # Filter model_df and reference_model_df for this cell
        # Need to merge with context to get cell_id
        model_with_context = pd.merge(
            model_df,
            context_with_cells,
            on=['_decision', '_choice'],
            how='inner'
        )

        reference_with_context = pd.merge(
            reference_model_df,
            context_with_cells,
            on=['_decision', '_choice'],
            how='inner'
        )

        # Filter to this cell
        cell_model_df = model_with_context[model_with_context['cell_id'] == cell_id]
        cell_reference_df = reference_with_context[reference_with_context['cell_id'] == cell_id]

        if len(cell_model_df) == 0:
            print(f"    Warning: No data for cell_id {cell_id}, skipping")
            continue

        # Compute mixtures for this cell
        cell_mixtures = compute_mixtures(
            cell_model_df,
            cell_reference_df,
            epsilons
        )

        # Build minimums for this cell
        minimums = build_minimums(cell_mixtures, minimums)

        # Build occupancy dataframe
        occupancy_df = build_occupancy(cell_mixtures)

        # Write occupancy parquet file
        occupancy_path = os.path.join(scenario_dir, f'{cell_id}_occupancy.parquet.gz')
        occupancy_df.to_parquet(occupancy_path, compression='gzip')

        if (cell_id + 1) % 10 == 0:
            print(f"    Processed {cell_id + 1}/{len(unique_cell_ids)} cells")

    print(f"  ✓ Wrote {len(unique_cell_ids)} occupancy files")

    # 10. Write minimums.json
    minimums_path = os.path.join(scenario_dir, 'minimums.json')
    with open(minimums_path, 'w') as f:
        json.dump(minimums, f, indent=2)
    print(f"  ✓ Wrote minimums.json")

    print(f"\n✓ Report build complete! Output in {scenario_dir}")
