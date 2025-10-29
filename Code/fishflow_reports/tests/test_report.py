"""Tests for fishflow.depth.report module."""

import os
import json
import tempfile
import shutil
import numpy as np
import pandas as pd
import pytest

from fishflow.depth.report import (
    build_minimums,
    build_occupancy,
    build_cell_depths,
    build_report
)


class TestBuildMinimums:
    """Tests for build_minimums function."""

    def test_basic_minimums(self):
        """Test basic minimums computation."""
        mixture_df = pd.DataFrame({
            'cell_id': [0, 0, 0, 0],
            'depth_bin': [10.0, 10.0, 10.0, 10.0],
            'datetime': [
                '2023-01-15 08:00:00',
                '2023-01-15 09:00:00',
                '2023-02-15 08:00:00',
                '2023-02-15 08:00:00',
            ],
            'probability': [0.5, 0.3, 0.6, 0.4],
            'epsilon': [1.0, 1.0, 1.0, 1.0]
        })

        minimums = build_minimums(mixture_df)

        # Check structure
        assert 0 in minimums
        assert 10.0 in minimums[0]
        assert 0 in minimums[0][10.0]  # January (month 0)
        assert 1 in minimums[0][10.0]  # February (month 1)

        # Check values
        assert minimums[0][10.0][0][8] == 0.5  # Jan, hour 8
        assert minimums[0][10.0][0][9] == 0.3  # Jan, hour 9
        assert minimums[0][10.0][1][8] == 0.4  # Feb, hour 8 (min of 0.6 and 0.4)

    def test_epsilon_filtering(self):
        """Test that only epsilon=1 is used."""
        mixture_df = pd.DataFrame({
            'cell_id': [0, 0],
            'depth_bin': [10.0, 10.0],
            'datetime': ['2023-01-15 08:00:00', '2023-01-15 08:00:00'],
            'probability': [0.5, 0.8],
            'epsilon': [1.0, 0.5]  # Different epsilons
        })

        minimums = build_minimums(mixture_df)

        # Should only use epsilon=1 (probability=0.5)
        assert minimums[0][10.0][0][8] == 0.5

    def test_update_existing_minimums(self):
        """Test updating existing minimums dict."""
        existing = {
            0: {
                10.0: {
                    0: [1.0] * 24
                }
            }
        }

        existing[0][10.0][0][8] = 0.6

        mixture_df = pd.DataFrame({
            'cell_id': [0],
            'depth_bin': [10.0],
            'datetime': ['2023-01-15 08:00:00'],
            'probability': [0.4],
            'epsilon': [1.0]
        })

        minimums = build_minimums(mixture_df, existing)

        # Should update to new minimum
        assert minimums[0][10.0][0][8] == 0.4


class TestBuildOccupancy:
    """Tests for build_occupancy function."""

    def test_basic_occupancy(self):
        """Test basic occupancy dataframe construction."""
        mixture_df = pd.DataFrame({
            'depth_bin': [10.0, 20.0, 10.0, 20.0],
            'datetime': ['2023-01-01', '2023-01-01', '2023-01-02', '2023-01-02'],
            'probability': [0.3, 0.7, 0.4, 0.6],
            'epsilon': [1.0, 1.0, 1.0, 1.0]
        })

        depth_bins = np.array([10.0, 20.0])
        occupancy = build_occupancy(mixture_df, depth_bins)

        # Check shape: 2 times, 2 depth bins, 1 epsilon = 2 columns
        assert occupancy.shape == (2, 2)

        # Check index is datetime
        assert len(occupancy.index) == 2

    def test_column_ordering(self):
        """Test that columns follow model_idx * n_depth_bins + depth_bin_idx."""
        mixture_df = pd.DataFrame({
            'depth_bin': [10.0, 20.0, 10.0, 20.0, 10.0, 20.0],
            'datetime': ['2023-01-01'] * 6,
            'probability': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
            'epsilon': [0.0, 0.0, 0.5, 0.5, 1.0, 1.0]
        })

        depth_bins = np.array([10.0, 20.0])
        occupancy = build_occupancy(mixture_df, depth_bins)

        # 3 epsilons, 2 depth bins = 6 columns
        assert occupancy.shape[1] == 6

        # Model 0 (eps=0), depth 0 (10.0) should be column 0
        assert occupancy.iloc[0, 0] == 0.1
        # Model 0, depth 1 (20.0) should be column 1
        assert occupancy.iloc[0, 1] == 0.2
        # Model 1 (eps=0.5), depth 0 should be column 2
        assert occupancy.iloc[0, 2] == 0.3
        # Model 1, depth 1 should be column 3
        assert occupancy.iloc[0, 3] == 0.4
        # Model 2 (eps=1.0), depth 0 should be column 4
        assert occupancy.iloc[0, 4] == 0.5
        # Model 2, depth 1 should be column 5
        assert occupancy.iloc[0, 5] == 0.6

    def test_missing_columns(self):
        """Test error on missing required columns."""
        bad_df = pd.DataFrame({
            'depth_bin': [10.0],
            'datetime': ['2023-01-01']
            # Missing probability and epsilon
        })

        depth_bins = np.array([10.0])
        with pytest.raises(ValueError, match="must have columns"):
            build_occupancy(bad_df, depth_bins)

    def test_missing_depth_bins(self):
        """Test that missing depth bins result in null columns."""
        mixture_df = pd.DataFrame({
            'depth_bin': [10.0, 10.0],  # Only depth bin 10.0 present
            'datetime': ['2023-01-01', '2023-01-02'],
            'probability': [0.3, 0.4],
            'epsilon': [1.0, 1.0]
        })

        # Provide depth bins that include one not in the mixture_df
        depth_bins = np.array([10.0, 20.0, 30.0])
        occupancy = build_occupancy(mixture_df, depth_bins)

        # Should have 2 times, 3 depth bins, 1 epsilon = 3 columns
        assert occupancy.shape == (2, 3)

        # First column (depth_bin 10.0) should have values
        assert occupancy.iloc[0, 0] == 0.3
        assert occupancy.iloc[1, 0] == 0.4

        # Second and third columns (depth_bins 20.0, 30.0) should be null
        assert pd.isna(occupancy.iloc[0, 1])
        assert pd.isna(occupancy.iloc[1, 1])
        assert pd.isna(occupancy.iloc[0, 2])
        assert pd.isna(occupancy.iloc[1, 2])


class TestBuildCellDepths:
    """Tests for build_cell_depths function."""

    def test_basic_cell_depths(self):
        """Test basic cell depths computation."""
        context_df = pd.DataFrame({
            'cell_id': [0, 0, 0, 1, 1],
            'depth_bin': [10.0, 20.0, 30.0, 10.0, 25.0]
        })

        cell_depths = build_cell_depths(context_df)

        assert cell_depths[0] == 30.0
        assert cell_depths[1] == 25.0

    def test_single_cell(self):
        """Test with single cell."""
        context_df = pd.DataFrame({
            'cell_id': [0, 0],
            'depth_bin': [10.0, 15.0]
        })

        cell_depths = build_cell_depths(context_df)

        assert len(cell_depths) == 1
        assert cell_depths[0] == 15.0

    def test_missing_columns(self):
        """Test error on missing columns."""
        bad_df = pd.DataFrame({'cell_id': [0]})

        with pytest.raises(ValueError, match="must have columns"):
            build_cell_depths(bad_df)


class TestBuildReport:
    """Integration tests for build_report function."""

    def create_test_data(self):
        """Create minimal test data for report building."""
        # Use valid H3 indices
        h3_indices = ['85283473fffffff', '8528347bfffffff']

        # Create context
        decisions = []
        choices = []
        datetimes = []
        h3_idx_list = []
        depth_bins = []

        for i, dt in enumerate(['2023-01-01 00:00:00', '2023-01-01 12:00:00']):
            for h3_idx in h3_indices:
                for depth in [10.0, 20.0]:
                    decisions.append(i * 10 + len(decisions))
                    choices.append('A')
                    datetimes.append(dt)
                    h3_idx_list.append(h3_idx)
                    depth_bins.append(depth)

        context_df = pd.DataFrame({
            '_decision': decisions,
            '_choice': choices,
            'datetime': datetimes,
            'h3_index': h3_idx_list,
            'depth_bin': depth_bins
        })

        # Create model predictions
        model_df = context_df[['_decision', '_choice']].copy()
        model_df['probability'] = np.random.dirichlet([1, 1], len(model_df))[:, 0]
        # Normalize by decision
        for dec in model_df['_decision'].unique():
            mask = model_df['_decision'] == dec
            total = model_df.loc[mask, 'probability'].sum()
            model_df.loc[mask, 'probability'] /= total

        # Create reference model (uniform)
        reference_df = model_df.copy()
        for dec in reference_df['_decision'].unique():
            mask = reference_df['_decision'] == dec
            n_choices = mask.sum()
            reference_df.loc[mask, 'probability'] = 1.0 / n_choices

        # Create actuals (smaller set)
        n_actuals = 4
        actual_decisions = list(range(n_actuals))
        actual_choices = ['A'] * n_actuals

        model_actuals = pd.DataFrame({
            '_decision': actual_decisions + actual_decisions,
            '_choice': actual_choices + ['B'] * n_actuals,
            'probability': [0.7, 0.3] * n_actuals
        })

        reference_actuals = pd.DataFrame({
            '_decision': actual_decisions + actual_decisions,
            '_choice': actual_choices + ['B'] * n_actuals,
            'probability': [0.5, 0.5] * n_actuals
        })

        selections_actuals = pd.DataFrame({
            '_decision': actual_decisions,
            '_choice': actual_choices
        })

        return (
            context_df,
            model_df,
            reference_df,
            model_actuals,
            reference_actuals,
            selections_actuals
        )

    def test_full_report_generation(self):
        """Test complete report generation."""
        (
            context_df,
            model_df,
            reference_df,
            model_actuals,
            reference_actuals,
            selections_actuals
        ) = self.create_test_data()

        meta_data = {
            'scenario_id': 'test_scenario',
            'name': 'Test Scenario',
            'species': 'Test Fish',
            'model': 'Complex Model',
            'reference_model': 'Uniform Model',
            'region': 'Test Region',
            'reference_region': 'Reference Region',
            'description': 'A test scenario',
            'reference_time_window': ['2023-01-01 00:00:00', '2023-01-31 23:59:59'],
            'zoom': 5,
            'center': [-122.4, 37.8]
        }

        epsilons = np.linspace(0, 1, 5)

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            build_report(
                meta_data,
                model_df,
                reference_df,
                context_df,
                model_actuals,
                reference_actuals,
                selections_actuals,
                epsilons,
                tmpdir
            )

            # Check that output directory exists
            output_dir = os.path.join(tmpdir, 'test_scenario')
            assert os.path.exists(output_dir)

            # Check all required files exist
            assert os.path.exists(os.path.join(output_dir, 'meta_data.json'))
            assert os.path.exists(os.path.join(output_dir, 'geometries.geojson'))
            assert os.path.exists(os.path.join(output_dir, 'timestamps.json'))
            assert os.path.exists(os.path.join(output_dir, 'cell_depths.json'))
            assert os.path.exists(os.path.join(output_dir, 'minimums.json'))

            # Check metadata
            with open(os.path.join(output_dir, 'meta_data.json')) as f:
                saved_meta = json.load(f)

            assert 'support' in saved_meta
            assert 'resolution' in saved_meta
            assert 'grid_size' in saved_meta
            assert 'depth_bins' in saved_meta
            assert 'time_window' in saved_meta

            # Check that occupancy files exist
            occupancy_files = [f for f in os.listdir(output_dir) if f.endswith('_occupancy.parquet.gz')]
            assert len(occupancy_files) > 0

    def test_missing_metadata(self):
        """Test error on missing required metadata."""
        (
            context_df,
            model_df,
            reference_df,
            model_actuals,
            reference_actuals,
            selections_actuals
        ) = self.create_test_data()

        incomplete_meta = {
            'scenario_id': 'test',
            'name': 'Test'
            # Missing many required fields
        }

        epsilons = np.array([0.0, 1.0])

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="missing required fields"):
                build_report(
                    incomplete_meta,
                    model_df,
                    reference_df,
                    context_df,
                    model_actuals,
                    reference_actuals,
                    selections_actuals,
                    epsilons,
                    tmpdir
                )
