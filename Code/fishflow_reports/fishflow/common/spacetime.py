"""
Spacetime utilities for FishFlow reports.

This module handles spatial (H3 hexagons) and temporal (timelines) aspects
of fish occupancy data.
"""

import h3
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any


def build_geojson_h3(context_df: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Build GeoJSON of H3 hexagons and map them to cell IDs.

    Creates a GeoJSON FeatureCollection of H3 hexagon polygons, assigning
    each unique H3 index a numeric cell_id. Also returns a mapping dataframe
    linking decisions/choices to their cell_ids.

    Args:
        context_df: DataFrame with at least columns '_decision', '_choice', 'h3_index'.

    Returns:
        Tuple of (geojson, cell_id_df) where:
        - geojson: GeoJSON FeatureCollection with H3 polygon features,
          each having a 'cell_id' property
        - cell_id_df: DataFrame with columns '_decision', '_choice', 'cell_id'
          mapping each decision-choice pair to its cell_id

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate input
    required_cols = {'_decision', '_choice', 'h3_index'}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(f"context_df must have columns {required_cols}")

    # Get unique H3 indices in alphabetical order
    unique_h3_indices = sorted(context_df['h3_index'].unique())

    # Create cell_id mapping (alphabetical order, starting from 0)
    h3_to_cell_id = {h3_index: i for i, h3_index in enumerate(unique_h3_indices)}

    # Build GeoJSON features
    features = []
    for h3_index in unique_h3_indices:
        cell_id = h3_to_cell_id[h3_index]

        # Get boundary coordinates from H3
        # h3.cell_to_boundary returns lat/lon pairs, we need lon/lat for GeoJSON
        boundary = h3.cell_to_boundary(h3_index)
        # Convert (lat, lon) to [lon, lat] and close the polygon
        coordinates = [[lon, lat] for lat, lon in boundary]
        # GeoJSON polygons should be closed (first point == last point)
        coordinates.append(coordinates[0])

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            },
            "properties": {
                "cell_id": cell_id
            }
        }
        features.append(feature)

    # Create GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    # Create cell_id dataframe
    cell_id_df = context_df[['_decision', '_choice', 'h3_index']].copy()
    cell_id_df['cell_id'] = cell_id_df['h3_index'].map(h3_to_cell_id)
    cell_id_df = cell_id_df.drop('h3_index', axis=1)

    return geojson, cell_id_df


def build_timeline(context_df: pd.DataFrame) -> np.ndarray:
    """
    Extract ordered timeline from context dataframe.

    Args:
        context_df: DataFrame with at least columns '_decision', '_choice', 'datetime'.

    Returns:
        Sorted array of unique datetime values.

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate input
    required_cols = {'_decision', '_choice', 'datetime'}
    if not required_cols.issubset(context_df.columns):
        raise ValueError(f"context_df must have columns {required_cols}")

    # Extract unique datetimes and sort
    timeline = sorted(context_df['datetime'].unique())

    return np.array(timeline)
