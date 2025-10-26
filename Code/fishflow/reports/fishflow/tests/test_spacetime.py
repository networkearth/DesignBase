"""
Unit tests for spacetime module.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from fishflow.common.spacetime import build_geojson_h3, build_timeline


class TestBuildGeojsonH3(unittest.TestCase):
    """Test build_geojson_h3 function."""

    def setUp(self):
        """Set up test fixtures."""
        # Use valid H3 indices (resolution 7)
        self.context_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'h3_index': ['87283080fffffff', '87283082fffffff', '87283080fffffff', '87283084fffffff']
        })

    def test_basic_functionality(self):
        """Test basic GeoJSON generation."""
        geojson_data, cell_id_df = build_geojson_h3(self.context_df)

        # Check that GeoJSON has correct structure
        self.assertIn('type', geojson_data)
        self.assertEqual(geojson_data['type'], 'FeatureCollection')
        self.assertIn('features', geojson_data)

        # Should have 3 unique H3 indices
        unique_h3 = self.context_df['h3_index'].nunique()
        self.assertEqual(len(geojson_data['features']), unique_h3)

        # Check cell_id_df structure
        self.assertIn('cell_id', cell_id_df.columns)
        self.assertIn('_decision', cell_id_df.columns)
        self.assertIn('_choice', cell_id_df.columns)

    def test_cell_id_ordering(self):
        """Test that cell_ids are assigned in alphabetical order of h3_index."""
        geojson_data, cell_id_df = build_geojson_h3(self.context_df)

        # Get unique h3 indices and sort them
        unique_h3_sorted = sorted(self.context_df['h3_index'].unique())

        # Check that cell_ids in GeoJSON are in order
        for i, feature in enumerate(geojson_data['features']):
            self.assertEqual(feature['properties']['cell_id'], i)

    def test_cell_id_mapping(self):
        """Test that cell_id_df correctly maps decisions and choices."""
        geojson_data, cell_id_df = build_geojson_h3(self.context_df)

        # Check that all original rows are present
        self.assertEqual(len(cell_id_df), len(self.context_df))

        # Check that cell_ids are integers starting from 0
        min_cell_id = cell_id_df['cell_id'].min()
        max_cell_id = cell_id_df['cell_id'].max()
        self.assertEqual(min_cell_id, 0)
        self.assertEqual(max_cell_id, self.context_df['h3_index'].nunique() - 1)

    def test_missing_columns(self):
        """Test that missing columns raise ValueError."""
        bad_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B']
        })
        with self.assertRaises(ValueError):
            build_geojson_h3(bad_df)


class TestBuildTimeline(unittest.TestCase):
    """Test build_timeline function."""

    def setUp(self):
        """Set up test fixtures."""
        self.context_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2, 3, 3],
            '_choice': ['A', 'B', 'A', 'B', 'A', 'B'],
            'datetime': [
                datetime(2024, 1, 1, 10, 0),
                datetime(2024, 1, 1, 10, 0),
                datetime(2024, 1, 1, 12, 0),
                datetime(2024, 1, 1, 12, 0),
                datetime(2024, 1, 1, 11, 0),
                datetime(2024, 1, 1, 11, 0),
            ]
        })

    def test_basic_functionality(self):
        """Test basic timeline extraction."""
        timeline = build_timeline(self.context_df)

        # Should return a list
        self.assertIsInstance(timeline, list)

        # Should have 3 unique datetimes
        self.assertEqual(len(timeline), 3)

    def test_sorted_order(self):
        """Test that timeline is sorted."""
        timeline = build_timeline(self.context_df)

        # Check that timeline is sorted
        for i in range(len(timeline) - 1):
            self.assertLessEqual(timeline[i], timeline[i + 1])

    def test_unique_values(self):
        """Test that timeline contains only unique values."""
        timeline = build_timeline(self.context_df)

        # Check uniqueness
        self.assertEqual(len(timeline), len(set(timeline)))

    def test_missing_columns(self):
        """Test that missing columns raise ValueError."""
        bad_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B']
        })
        with self.assertRaises(ValueError):
            build_timeline(bad_df)


if __name__ == '__main__':
    unittest.main()
