"""
Spacetime functions for handling spatial (H3) and temporal data transformations.

This module provides utilities for working with H3 hexagonal spatial indices
and time series data.
"""

import h3
import pandas as pd
import numpy as np
from typing import Dict, Tuple


def build_geojson_h3(context_df: pd.DataFrame) -> Tuple[Dict, pd.DataFrame]:
    """
    Build a GeoJSON representation of H3 cells and a mapping from decision/choice to cell_id.

    Args:
        context_df: DataFrame with at least columns '_decision', '_choice', and 'h3_index'.
            The h3_index column contains H3 hexagonal cell indices.

    Returns:
        Tuple of (geojson, cell_id_df):
            - geojson: A GeoJSON FeatureCollection with Polygon features for each unique
              H3 cell. Each feature has a 'cell_id' property (integer starting from 0).
            - cell_id_df: DataFrame with columns '_decision', '_choice', 'cell_id' mapping
              each decision/choice pair to its corresponding cell_id.

    Raises:
        ValueError: If required columns are missing or h3_index values are invalid.
    """
    # Validate required columns
    required_cols = {'_decision', '_choice', 'h3_index'}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(f"context_df must have columns: {required_cols}")

    # Get unique H3 indices in alphabetical order
    unique_h3_indices = sorted(context_df['h3_index'].unique())

    if len(unique_h3_indices) == 0:
        raise ValueError("context_df must have at least one h3_index")

    # Create mapping from h3_index to cell_id (integers starting from 0)
    h3_to_cell_id = {h3_idx: i for i, h3_idx in enumerate(unique_h3_indices)}

    # Build cell_id_df by mapping h3_index to cell_id
    cell_id_df = context_df[['_decision', '_choice', 'h3_index']].copy()
    cell_id_df['cell_id'] = cell_id_df['h3_index'].map(h3_to_cell_id)
    cell_id_df = cell_id_df[['_decision', '_choice', 'cell_id']]

    # Build GeoJSON features for each unique H3 cell
    features = []

    for h3_index, cell_id in h3_to_cell_id.items():
        try:
            # Get boundary as list of (lat, lon) tuples
            boundary = h3.cell_to_boundary(h3_index)

            # Convert to GeoJSON coordinates format: [[lon, lat], ...]
            # Note: GeoJSON uses [lon, lat] order, and we need to close the polygon
            coordinates = [[lon, lat] for lat, lon in boundary]
            coordinates.append(coordinates[0])  # Close the polygon

            # Create GeoJSON feature
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]  # Array of rings (just one outer ring)
                },
                "properties": {
                    "cell_id": cell_id
                }
            }

            features.append(feature)

        except Exception as e:
            raise ValueError(f"Invalid h3_index '{h3_index}': {str(e)}")

    # Build GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return geojson, cell_id_df


def build_timeline(context_df: pd.DataFrame) -> list:
    """
    Extract and sort unique datetime values from context dataframe.

    Args:
        context_df: DataFrame with at least columns '_decision', '_choice', and 'datetime'.
            The datetime column should contain timestamp values.

    Returns:
        Sorted list of unique datetime values (earliest first).

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate required columns
    required_cols = {'_decision', '_choice', 'datetime'}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(f"context_df must have columns: {required_cols}")

    # Get unique datetime values
    unique_datetimes = context_df['datetime'].unique()

    if len(unique_datetimes) == 0:
        raise ValueError("context_df must have at least one datetime value")

    # Convert to pandas datetime if not already
    unique_datetimes = pd.to_datetime(unique_datetimes)

    # Sort and convert to list
    timeline = sorted(unique_datetimes)

    # Convert to ISO format strings for JSON serialization
    timeline = [dt.isoformat() for dt in timeline]

    return timeline
