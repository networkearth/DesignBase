"""
Spacetime utilities for FishFlow reports.

This module provides functions for working with spatial (H3) and temporal data.
"""

import h3
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any


def build_geojson_h3(context_df: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Build GeoJSON and cell ID mapping from H3 indices.

    Converts H3 indices in the context dataframe to GeoJSON polygons
    and creates a mapping from decision-choice pairs to numeric cell IDs.

    Args:
        context_df: DataFrame with at least columns ['_decision', '_choice', 'h3_index'].

    Returns:
        Tuple of (geojson, cell_id_df):
            - geojson: A GeoJSON FeatureCollection of H3 polygons with cell_id properties
            - cell_id_df: DataFrame with columns ['_decision', '_choice', 'cell_id']
              where cell_id corresponds to the original h3_index

    Raises:
        ValueError: If required columns are missing from context_df.
    """
    # Validate required columns
    required_cols = {"_decision", "_choice", "h3_index"}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(
            f"context_df must contain columns: {required_cols}, "
            f"but has: {context_df.columns.tolist()}"
        )

    # Get unique h3 indices and sort them alphabetically
    unique_h3_indices = sorted(context_df["h3_index"].unique())

    # Create mapping from h3_index to cell_id (starting at 0)
    h3_to_cell_id = {h3_idx: i for i, h3_idx in enumerate(unique_h3_indices)}

    # Build GeoJSON features for each unique H3 cell
    features = []
    for h3_idx in unique_h3_indices:
        # Get boundary coordinates for this H3 cell
        boundary = h3.cell_to_boundary(h3_idx)

        # Convert boundary to GeoJSON coordinate format (lon, lat)
        # h3.cell_to_boundary returns (lat, lon) tuples, so we need to swap
        coordinates = [[[lon, lat] for lat, lon in boundary]]

        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": coordinates},
            "properties": {"cell_id": h3_to_cell_id[h3_idx]},
        }
        features.append(feature)

    # Create GeoJSON FeatureCollection
    geojson = {"type": "FeatureCollection", "features": features}

    # Create cell_id dataframe
    cell_id_df = context_df[["_decision", "_choice", "h3_index"]].copy()
    cell_id_df["cell_id"] = cell_id_df["h3_index"].map(h3_to_cell_id)
    cell_id_df = cell_id_df[["_decision", "_choice", "cell_id"]]

    return geojson, cell_id_df


def build_timeline(context_df: pd.DataFrame) -> np.ndarray:
    """
    Extract ordered timeline from context dataframe.

    Pulls unique datetime values from the context and returns them in sorted order.

    Args:
        context_df: DataFrame with at least columns ['_decision', '_choice', 'datetime'].

    Returns:
        Array of unique datetime values in sorted order.

    Raises:
        ValueError: If required columns are missing from context_df.
    """
    # Validate required columns
    required_cols = {"_decision", "_choice", "datetime"}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(
            f"context_df must contain columns: {required_cols}, "
            f"but has: {context_df.columns.tolist()}"
        )

    # Get unique datetime values and sort them
    timeline = sorted(context_df["datetime"].unique())

    # Convert to numpy array
    timeline = np.array(timeline)

    return timeline
