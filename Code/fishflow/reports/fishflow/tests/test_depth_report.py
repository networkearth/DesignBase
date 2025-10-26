"""
Unit tests for depth report module.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from fishflow.depth.report import (
    build_cell_depths,
    build_occupancy,
    build_minimums
)


class TestBuildCellDepths(unittest.TestCase):
    """Test build_cell_depths function."""

    def setUp(self):
        """Set up test fixtures."""
        self.context_df = pd.DataFrame({
            'cell_id': [0, 0, 0, 1, 1, 2],
            'depth_bin': [1, 2, 3, 1, 2, 1]
        })

    def test_basic_functionality(self):
        """Test basic cell depth extraction."""
        cell_depths = build_cell_depths(self.context_df)

        # Should return a dictionary
        self.assertIsInstance(cell_depths, dict)

        # Should have 3 cells
        self.assertEqual(len(cell_depths), 3)

        # Check maximum depths
        self.assertEqual(cell_depths[0], 3)
        self.assertEqual(cell_depths[1], 2)
        self.assertEqual(cell_depths[2], 1)

    def test_integer_types(self):
        """Test that returned values are integers."""
        cell_depths = build_cell_depths(self.context_df)

        for cell_id, depth in cell_depths.items():
            self.assertIsInstance(cell_id, int)
            self.assertIsInstance(depth, int)

    def test_missing_columns(self):
        """Test that missing columns raise ValueError."""
        bad_df = pd.DataFrame({
            'cell_id': [0, 1, 2]
        })
        with self.assertRaises(ValueError):
            build_cell_depths(bad_df)


class TestBuildOccupancy(unittest.TestCase):
    """Test build_occupancy function."""

    def setUp(self):
        """Set up test fixtures."""
        datetimes = [
            datetime(2024, 1, 1, 10, 0),
            datetime(2024, 1, 1, 11, 0),
            datetime(2024, 1, 1, 12, 0)
        ]
        epsilons = [0.0, 1.0]
        depth_bins = [1, 2]

        # Create all combinations
        data = []
        for dt in datetimes:
            for eps in epsilons:
                for db in depth_bins:
                    data.append({
                        'datetime': dt,
                        'epsilon': eps,
                        'depth_bin': db,
                        'probability': np.random.random()
                    })

        self.mixture_df = pd.DataFrame(data)

    def test_basic_functionality(self):
        """Test basic occupancy matrix construction."""
        occupancy_df = build_occupancy(self.mixture_df)

        # Should return a DataFrame
        self.assertIsInstance(occupancy_df, pd.DataFrame)

        # Number of rows should match number of unique datetimes
        n_datetimes = self.mixture_df['datetime'].nunique()
        self.assertEqual(len(occupancy_df), n_datetimes)

        # Number of columns should be num_epsilons * num_depth_bins
        n_epsilons = self.mixture_df['epsilon'].nunique()
        n_depth_bins = self.mixture_df['depth_bin'].nunique()
        self.assertEqual(occupancy_df.shape[1], n_epsilons * n_depth_bins)

    def test_column_indexing(self):
        """Test that column indexing follows the specified formula."""
        occupancy_df = build_occupancy(self.mixture_df)

        epsilons = sorted(self.mixture_df['epsilon'].unique())
        depth_bins = sorted(self.mixture_df['depth_bin'].unique())
        num_depth_bins = len(depth_bins)

        # Get first datetime
        first_dt = sorted(self.mixture_df['datetime'].unique())[0]

        # Check a few column values
        for model_idx, eps in enumerate(epsilons):
            for depth_bin_idx, db in enumerate(depth_bins):
                col_idx = model_idx * num_depth_bins + depth_bin_idx

                # Get expected probability from mixture_df
                expected_prob = self.mixture_df[
                    (self.mixture_df['datetime'] == first_dt) &
                    (self.mixture_df['epsilon'] == eps) &
                    (self.mixture_df['depth_bin'] == db)
                ]['probability'].iloc[0]

                # Get actual probability from occupancy
                actual_prob = occupancy_df.iloc[0, col_idx]

                self.assertAlmostEqual(actual_prob, expected_prob)

    def test_missing_columns(self):
        """Test that missing columns raise ValueError."""
        bad_df = pd.DataFrame({
            'datetime': [datetime(2024, 1, 1)],
            'epsilon': [0.5]
        })
        with self.assertRaises(ValueError):
            build_occupancy(bad_df)


class TestBuildMinimums(unittest.TestCase):
    """Test build_minimums function."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test data with known minimums
        self.mixture_df = pd.DataFrame({
            'cell_id': [0, 0, 0, 0, 0, 0],
            'depth_bin': [1, 1, 1, 2, 2, 2],
            'datetime': [
                datetime(2024, 1, 15, 10, 30),  # Month 0 (Jan), Hour 10
                datetime(2024, 1, 15, 11, 30),  # Month 0 (Jan), Hour 11
                datetime(2024, 2, 15, 10, 30),  # Month 1 (Feb), Hour 10
                datetime(2024, 1, 15, 10, 30),  # Month 0 (Jan), Hour 10
                datetime(2024, 1, 15, 11, 30),  # Month 0 (Jan), Hour 11
                datetime(2024, 2, 15, 10, 30),  # Month 1 (Feb), Hour 10
            ],
            'probability': [0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
            'epsilon': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        })

    def test_basic_functionality(self):
        """Test basic minimum computation."""
        minimums = build_minimums(self.mixture_df)

        # Should return a dictionary
        self.assertIsInstance(minimums, dict)

        # Should have cell 0
        self.assertIn(0, minimums)

        # Check structure: cell -> depth_bin -> month -> hour -> probability
        self.assertIn(1, minimums[0])
        self.assertIn(0, minimums[0][1])
        self.assertIn(10, minimums[0][1][0])

    def test_minimum_values(self):
        """Test that minimum values are correctly computed."""
        minimums = build_minimums(self.mixture_df)

        # For depth_bin 1, month 0 (Jan), hour 10: min of [0.3] = 0.3
        self.assertAlmostEqual(minimums[0][1][0][10], 0.3)

        # For depth_bin 1, month 0 (Jan), hour 11: min of [0.4] = 0.4
        self.assertAlmostEqual(minimums[0][1][0][11], 0.4)

        # For depth_bin 2, month 0 (Jan), hour 10: min of [0.6] = 0.6
        self.assertAlmostEqual(minimums[0][2][0][10], 0.6)

    def test_epsilon_filtering(self):
        """Test that only epsilon=1 data is used."""
        # Add some epsilon=0 data
        extra_data = pd.DataFrame({
            'cell_id': [0],
            'depth_bin': [1],
            'datetime': [datetime(2024, 1, 15, 10, 30)],
            'probability': [0.1],  # Lower than existing 0.3
            'epsilon': [0.0]
        })
        mixture_df = pd.concat([self.mixture_df, extra_data], ignore_index=True)

        minimums = build_minimums(mixture_df)

        # Should still be 0.3, not 0.1 (epsilon=0 should be filtered out)
        self.assertAlmostEqual(minimums[0][1][0][10], 0.3)

    def test_updating_existing_minimums(self):
        """Test that existing minimums dictionary is properly updated."""
        # Create initial minimums
        initial_minimums = {0: {1: {0: {10: 0.2}}}}

        # Build minimums should update this
        updated = build_minimums(self.mixture_df, minimums=initial_minimums)

        # Should still have the original value
        self.assertAlmostEqual(updated[0][1][0][10], 0.2)

        # Should also have new values
        self.assertIn(11, updated[0][1][0])

    def test_missing_columns(self):
        """Test that missing columns raise ValueError."""
        bad_df = pd.DataFrame({
            'cell_id': [0],
            'depth_bin': [1]
        })
        with self.assertRaises(ValueError):
            build_minimums(bad_df)


if __name__ == '__main__':
    unittest.main()
