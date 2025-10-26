"""
Unit tests for spacetime module functions.
"""

import pytest
import pandas as pd
import numpy as np
from fishflow.common.spacetime import build_geojson_h3, build_timeline


class TestBuildGeojsonH3:
    """Tests for build_geojson_h3 function."""

    def test_basic_geojson_construction(self):
        """Should create valid GeoJSON from H3 indices."""
        context_df = pd.DataFrame({
            '_decision': [1, 1, 2],
            '_choice': ['A', 'B', 'A'],
            'h3_index': ['85283473fffffff', '85283473fffffff', '8528342bfffffff']
        })

        geojson, cell_id_df = build_geojson_h3(context_df)

        # Check GeoJSON structure
        assert geojson['type'] == 'FeatureCollection'
        assert 'features' in geojson
        assert len(geojson['features']) == 2  # Two unique H3 cells

        # Check features have correct structure
        for feature in geojson['features']:
            assert feature['type'] == 'Feature'
            assert feature['geometry']['type'] == 'Polygon'
            assert 'cell_id' in feature['properties']

        # Check cell_id_df
        assert len(cell_id_df) == 3
        assert set(cell_id_df.columns) == {'_decision', '_choice', 'cell_id'}
        assert cell_id_df['cell_id'].dtype in [np.int32, np.int64]

    def test_cell_ids_start_from_zero(self):
        """Cell IDs should start from 0."""
        context_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A'],
            'h3_index': ['85283473fffffff']
        })

        geojson, cell_id_df = build_geojson_h3(context_df)

        assert cell_id_df['cell_id'].min() == 0

    def test_cell_ids_alphabetical_order(self):
        """Cell IDs should be assigned in alphabetical order of H3 indices."""
        # Use H3 indices that are clearly alphabetically ordered
        context_df = pd.DataFrame({
            '_decision': [1, 2, 3],
            '_choice': ['A', 'B', 'C'],
            'h3_index': ['8528342bfffffff', '85283473fffffff', '85283447fffffff']
        })

        geojson, cell_id_df = build_geojson_h3(context_df)

        # Merge to check order
        merged = cell_id_df.merge(
            context_df[['_decision', '_choice', 'h3_index']],
            on=['_decision', '_choice']
        )

        sorted_h3 = sorted(merged['h3_index'].unique())
        for i, h3_idx in enumerate(sorted_h3):
            cell_id = merged[merged['h3_index'] == h3_idx]['cell_id'].iloc[0]
            assert cell_id == i

    def test_missing_columns_raises_error(self):
        """Should raise error if required columns are missing."""
        context_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A']
            # Missing h3_index
        })

        with pytest.raises(ValueError, match="must have columns"):
            build_geojson_h3(context_df)

    def test_polygon_is_closed(self):
        """GeoJSON polygons should be closed (first point == last point)."""
        context_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A'],
            'h3_index': ['85283473fffffff']
        })

        geojson, _ = build_geojson_h3(context_df)

        for feature in geojson['features']:
            coords = feature['geometry']['coordinates'][0]
            assert coords[0] == coords[-1]  # First and last points should match


class TestBuildTimeline:
    """Tests for build_timeline function."""

    def test_basic_timeline_extraction(self):
        """Should extract and sort unique datetime values."""
        context_df = pd.DataFrame({
            '_decision': [1, 2, 3],
            '_choice': ['A', 'B', 'C'],
            'datetime': ['2023-01-01T12:00:00', '2023-01-01T10:00:00', '2023-01-01T14:00:00']
        })

        timeline = build_timeline(context_df)

        assert len(timeline) == 3
        assert timeline == sorted(timeline)  # Should be sorted
        # Check first and last
        assert timeline[0] == '2023-01-01T10:00:00'
        assert timeline[-1] == '2023-01-01T14:00:00'

    def test_removes_duplicates(self):
        """Should return only unique datetime values."""
        context_df = pd.DataFrame({
            '_decision': [1, 2, 3],
            '_choice': ['A', 'B', 'C'],
            'datetime': ['2023-01-01T12:00:00', '2023-01-01T12:00:00', '2023-01-01T14:00:00']
        })

        timeline = build_timeline(context_df)

        assert len(timeline) == 2  # Only 2 unique datetimes

    def test_handles_datetime_objects(self):
        """Should handle pandas datetime objects."""
        context_df = pd.DataFrame({
            '_decision': [1, 2],
            '_choice': ['A', 'B'],
            'datetime': pd.to_datetime(['2023-01-01 12:00:00', '2023-01-02 12:00:00'])
        })

        timeline = build_timeline(context_df)

        assert len(timeline) == 2
        assert isinstance(timeline[0], str)  # Should be ISO format strings

    def test_missing_columns_raises_error(self):
        """Should raise error if required columns are missing."""
        context_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A']
            # Missing datetime
        })

        with pytest.raises(ValueError, match="must have columns"):
            build_timeline(context_df)
