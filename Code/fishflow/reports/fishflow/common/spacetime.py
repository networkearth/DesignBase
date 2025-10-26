"""
Spacetime utilities for building geospatial and temporal representations.

This module provides functions for extracting and formatting spatial (H3 hexagons)
and temporal (timeline) information from context dataframes.
"""

import pandas as pd
import h3
import geojson
from typing import Tuple, Dict, Any


def build_geojson_h3(context_df: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Build a GeoJSON representation of H3 hexagons from context data.

    This function extracts unique H3 indices from the context dataframe,
    creates polygon geometries for each, and assigns integer cell IDs in
    alphabetical order.

    Args:
        context_df: DataFrame with at least columns ['_decision', '_choice', 'h3_index'].

    Returns:
        Tuple of (geojson_dict, cell_id_df) where:
        - geojson_dict: A GeoJSON FeatureCollection with polygon features for
          each unique H3 index, including a 'cell_id' property.
        - cell_id_df: DataFrame with columns ['_decision', '_choice', 'cell_id']
          mapping each decision-choice pair to its integer cell ID.

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate required columns
    required_cols = ['_decision', '_choice', 'h3_index']
    if not all(col in context_df.columns for col in required_cols):
        raise ValueError(f"context_df must have columns {required_cols}")

    # Get unique H3 indices in alphabetical order
    unique_h3 = sorted(context_df['h3_index'].unique())

    # Create mapping from h3_index to cell_id (integer starting from 0)
    h3_to_cell_id = {h3_idx: i for i, h3_idx in enumerate(unique_h3)}

    # Build GeoJSON features
    features = []
    for h3_idx in unique_h3:
        cell_id = h3_to_cell_id[h3_idx]

        # Get the boundary coordinates for the H3 hexagon
        # h3.cell_to_boundary returns list of (lat, lon) tuples
        boundary = h3.cell_to_boundary(h3_idx, geo_json=True)

        # Create polygon geometry (GeoJSON uses [lon, lat] order)
        polygon = geojson.Polygon([boundary])

        # Create feature with cell_id property
        feature = geojson.Feature(
            geometry=polygon,
            properties={'cell_id': cell_id}
        )
        features.append(feature)

    # Create FeatureCollection
    feature_collection = geojson.FeatureCollection(features)

    # Create cell_id dataframe
    cell_id_df = context_df[['_decision', '_choice', 'h3_index']].copy()
    cell_id_df['cell_id'] = cell_id_df['h3_index'].map(h3_to_cell_id)
    cell_id_df = cell_id_df[['_decision', '_choice', 'cell_id']]

    return feature_collection, cell_id_df


def build_timeline(context_df: pd.DataFrame) -> list:
    """
    Extract and sort unique datetime values from context data.

    Args:
        context_df: DataFrame with at least columns ['_decision', '_choice', 'datetime'].

    Returns:
        Sorted list of unique datetime values.

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate required columns
    required_cols = ['_decision', '_choice', 'datetime']
    if not all(col in context_df.columns for col in required_cols):
        raise ValueError(f"context_df must have columns {required_cols}")

    # Get unique datetimes and sort them
    unique_datetimes = context_df['datetime'].unique()
    timeline = sorted(unique_datetimes)

    return timeline
