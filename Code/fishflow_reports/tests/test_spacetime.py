"""Tests for fishflow.common.spacetime module."""

import numpy as np
import pandas as pd
import pytest
import h3

from fishflow.common.spacetime import build_geojson_h3, build_timeline


class TestBuildGeojsonH3:
    """Tests for build_geojson_h3 function."""

    def test_basic_geojson_creation(self):
        """Test basic GeoJSON and cell_id creation."""
        # Create test data with valid H3 indices
        # Using resolution 5 H3 indices for San Francisco area
        h3_indices = [
            '85283473fffffff',  # Valid H3 index
            '8528347bfffffff',  # Another valid H3 index
        ]

        context_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'h3_index': [h3_indices[0], h3_indices[1], h3_indices[0], h3_indices[1]]
        })

        geojson, cell_id_df = build_geojson_h3(context_df)

        # Check GeoJSON structure
        assert geojson['type'] == 'FeatureCollection'
        assert 'features' in geojson
        assert len(geojson['features']) == 2  # Two unique H3 indices

        # Check each feature
        for feature in geojson['features']:
            assert feature['type'] == 'Feature'
            assert feature['geometry']['type'] == 'Polygon'
            assert 'cell_id' in feature['properties']
            assert isinstance(feature['properties']['cell_id'], int)

            # Check polygon is closed
            coords = feature['geometry']['coordinates'][0]
            assert coords[0] == coords[-1]

        # Check cell_id_df
        assert len(cell_id_df) == 4
        assert set(cell_id_df.columns) == {'_decision', '_choice', 'cell_id'}
        assert cell_id_df['cell_id'].min() == 0
        assert cell_id_df['cell_id'].max() == 1

    def test_alphabetical_ordering(self):
        """Test that cell_ids follow alphabetical order of h3_indices."""
        h3_indices = ['85283473fffffff', '8528340bfffffff', '85283477fffffff']
        sorted_indices = sorted(h3_indices)

        context_df = pd.DataFrame({
            '_decision': [1, 2, 3],
            '_choice': ['A', 'A', 'A'],
            'h3_index': h3_indices
        })

        geojson, cell_id_df = build_geojson_h3(context_df)

        # Create mapping from h3 to cell_id
        h3_to_cell = context_df.merge(cell_id_df, on=['_decision', '_choice'])
        h3_to_cell = h3_to_cell[['h3_index', 'cell_id']].drop_duplicates()

        # Check alphabetical ordering
        for i, h3_idx in enumerate(sorted_indices):
            cell_id = h3_to_cell[h3_to_cell['h3_index'] == h3_idx]['cell_id'].values[0]
            assert cell_id == i

    def test_missing_columns(self):
        """Test error on missing required columns."""
        bad_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A']
            # Missing h3_index
        })

        with pytest.raises(ValueError, match="must have columns"):
            build_geojson_h3(bad_df)

    def test_cell_id_consistency(self):
        """Test that same h3_index gets same cell_id."""
        h3_idx = '85283473fffffff'

        context_df = pd.DataFrame({
            '_decision': [1, 2, 3],
            '_choice': ['A', 'B', 'C'],
            'h3_index': [h3_idx, h3_idx, h3_idx]
        })

        _, cell_id_df = build_geojson_h3(context_df)

        # All rows should have same cell_id
        assert cell_id_df['cell_id'].nunique() == 1


class TestBuildTimeline:
    """Tests for build_timeline function."""

    def test_basic_timeline(self):
        """Test basic timeline extraction."""
        datetimes = [
            '2023-01-01 00:00:00',
            '2023-01-01 12:00:00',
            '2023-01-02 00:00:00',
            '2023-01-01 00:00:00',  # Duplicate
        ]

        context_df = pd.DataFrame({
            '_decision': [1, 2, 3, 4],
            '_choice': ['A', 'A', 'A', 'B'],
            'datetime': datetimes
        })

        timeline = build_timeline(context_df)

        # Should have 3 unique timestamps
        assert len(timeline) == 3

        # Should be sorted
        assert list(timeline) == sorted(timeline)

        # Check no duplicates
        assert len(timeline) == len(set(timeline))

    def test_timeline_ordering(self):
        """Test that timeline is properly sorted."""
        datetimes = [
            '2023-03-01',
            '2023-01-01',
            '2023-02-01',
        ]

        context_df = pd.DataFrame({
            '_decision': [1, 2, 3],
            '_choice': ['A', 'A', 'A'],
            'datetime': datetimes
        })

        timeline = build_timeline(context_df)

        expected_order = ['2023-01-01', '2023-02-01', '2023-03-01']
        assert list(timeline) == expected_order

    def test_missing_columns(self):
        """Test error on missing required columns."""
        bad_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A']
            # Missing datetime
        })

        with pytest.raises(ValueError, match="must have columns"):
            build_timeline(bad_df)

    def test_single_timestamp(self):
        """Test with single timestamp."""
        context_df = pd.DataFrame({
            '_decision': [1, 2],
            '_choice': ['A', 'B'],
            'datetime': ['2023-01-01', '2023-01-01']
        })

        timeline = build_timeline(context_df)

        assert len(timeline) == 1
        assert timeline[0] == '2023-01-01'
