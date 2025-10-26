"""
Unit tests for depth report module functions.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import json
from fishflow.depth.report import (
    build_cell_depths,
    build_occupancy,
    build_minimums,
    build_report
)


class TestBuildCellDepths:
    """Tests for build_cell_depths function."""

    def test_basic_depth_extraction(self):
        """Should find max depth_bin per cell_id."""
        context_df = pd.DataFrame({
            'cell_id': [0, 0, 1, 1, 1],
            'depth_bin': [0, 1, 0, 1, 2]
        })

        cell_depths = build_cell_depths(context_df)

        assert cell_depths[0] == 1
        assert cell_depths[1] == 2

    def test_single_cell(self):
        """Should handle single cell correctly."""
        context_df = pd.DataFrame({
            'cell_id': [5, 5],
            'depth_bin': [3, 7]
        })

        cell_depths = build_cell_depths(context_df)

        assert len(cell_depths) == 1
        assert cell_depths[5] == 7

    def test_missing_columns_raises_error(self):
        """Should raise error if required columns are missing."""
        context_df = pd.DataFrame({
            'cell_id': [0]
            # Missing depth_bin
        })

        with pytest.raises(ValueError, match="must have columns"):
            build_cell_depths(context_df)


class TestBuildOccupancy:
    """Tests for build_occupancy function."""

    def test_basic_occupancy_construction(self):
        """Should construct occupancy matrix correctly."""
        mixture_df = pd.DataFrame({
            'datetime': ['2023-01-01T10:00:00', '2023-01-01T10:00:00',
                        '2023-01-01T11:00:00', '2023-01-01T11:00:00'],
            'depth_bin': [0, 1, 0, 1],
            'epsilon': [0.0, 0.0, 0.0, 0.0],
            'probability': [0.6, 0.4, 0.7, 0.3]
        })

        occupancy_df = build_occupancy(mixture_df)

        # Should have 2 rows (2 unique datetimes)
        assert len(occupancy_df) == 2

        # Should have 2 columns (1 model * 2 depth bins)
        assert occupancy_df.shape[1] == 2

        # Check values
        assert occupancy_df.iloc[0, 0] == 0.6  # First datetime, depth_bin 0
        assert occupancy_df.iloc[0, 1] == 0.4  # First datetime, depth_bin 1

    def test_multiple_models(self):
        """Should handle multiple epsilon values correctly."""
        mixture_df = pd.DataFrame({
            'datetime': ['2023-01-01T10:00:00'] * 4,
            'depth_bin': [0, 1, 0, 1],
            'epsilon': [0.0, 0.0, 1.0, 1.0],
            'probability': [0.5, 0.5, 0.8, 0.2]
        })

        occupancy_df = build_occupancy(mixture_df)

        # Should have 1 row (1 datetime)
        assert len(occupancy_df) == 1

        # Should have 4 columns (2 models * 2 depth bins)
        assert occupancy_df.shape[1] == 4

        # Check column indexing: col = model_idx * num_depth_bins + depth_bin_idx
        # model_idx=0 (epsilon=0.0), depth_bin_idx=0
        assert occupancy_df.iloc[0, 0] == 0.5
        # model_idx=0 (epsilon=0.0), depth_bin_idx=1
        assert occupancy_df.iloc[0, 1] == 0.5
        # model_idx=1 (epsilon=1.0), depth_bin_idx=0
        assert occupancy_df.iloc[0, 2] == 0.8
        # model_idx=1 (epsilon=1.0), depth_bin_idx=1
        assert occupancy_df.iloc[0, 3] == 0.2

    def test_datetimes_sorted(self):
        """Datetimes should be sorted in output."""
        mixture_df = pd.DataFrame({
            'datetime': ['2023-01-01T14:00:00', '2023-01-01T10:00:00',
                        '2023-01-01T12:00:00'],
            'depth_bin': [0, 0, 0],
            'epsilon': [0.5, 0.5, 0.5],
            'probability': [0.3, 0.1, 0.2]
        })

        occupancy_df = build_occupancy(mixture_df)

        # Check index is sorted
        assert list(occupancy_df.index) == sorted(occupancy_df.index)
        assert occupancy_df.iloc[0, 0] == 0.1  # Earliest datetime

    def test_missing_columns_raises_error(self):
        """Should raise error if required columns are missing."""
        mixture_df = pd.DataFrame({
            'datetime': ['2023-01-01'],
            'depth_bin': [0]
            # Missing probability and epsilon
        })

        with pytest.raises(ValueError, match="must have columns"):
            build_occupancy(mixture_df)


class TestBuildMinimums:
    """Tests for build_minimums function."""

    def test_basic_minimums_computation(self):
        """Should compute minimums correctly."""
        mixture_df = pd.DataFrame({
            'cell_id': [0, 0, 0, 0],
            'depth_bin': [0, 0, 1, 1],
            'datetime': pd.to_datetime([
                '2023-01-15 10:00:00',  # Month 0, Hour 10
                '2023-01-15 10:30:00',  # Month 0, Hour 10
                '2023-01-15 11:00:00',  # Month 0, Hour 11
                '2023-01-15 11:30:00'   # Month 0, Hour 11
            ]),
            'epsilon': [1.0, 1.0, 1.0, 1.0],
            'probability': [0.6, 0.4, 0.7, 0.5]
        })

        minimums = build_minimums(mixture_df)

        # Should have structure: cell_id -> depth_bin -> month -> minimums_array
        assert 0 in minimums
        assert 0 in minimums[0]
        assert 1 in minimums[0]
        assert 0 in minimums[0][0]  # Month 0
        assert isinstance(minimums[0][0][0], list)  # Should be an array
        assert len(minimums[0][0][0]) == 24  # 24 hours

        # Check minimum values at specific hours
        assert minimums[0][0][0][10] == 0.4  # Min of 0.6 and 0.4
        assert minimums[0][1][0][11] == 0.5  # Min of 0.7 and 0.5

    def test_filters_epsilon_one_only(self):
        """Should only use epsilon=1.0 (non-reference model)."""
        mixture_df = pd.DataFrame({
            'cell_id': [0, 0],
            'depth_bin': [0, 0],
            'datetime': pd.to_datetime(['2023-01-15 10:00:00', '2023-01-15 10:00:00']),
            'epsilon': [0.0, 1.0],
            'probability': [0.1, 0.9]  # epsilon=0 has lower value but should be ignored
        })

        minimums = build_minimums(mixture_df)

        # Should use epsilon=1 value (0.9), not epsilon=0 value (0.1)
        # Month 0 should be an array, access hour 10
        assert isinstance(minimums[0][0][0], list)
        assert minimums[0][0][0][10] == 0.9

    def test_updates_existing_minimums(self):
        """Should update existing minimums dictionary."""
        # Create existing structure with array format
        existing_array = [float('inf')] * 24
        existing_array[10] = 0.5
        existing = {
            0: {
                0: {
                    0: existing_array
                }
            }
        }

        mixture_df = pd.DataFrame({
            'cell_id': [1],
            'depth_bin': [0],
            'datetime': pd.to_datetime(['2023-02-15 14:00:00']),  # Month 1, Hour 14
            'epsilon': [1.0],
            'probability': [0.8]
        })

        minimums = build_minimums(mixture_df, existing)

        # Should keep existing data
        assert minimums[0][0][0][10] == 0.5
        # Should add new data
        assert isinstance(minimums[1][0][1], list)
        assert minimums[1][0][1][14] == 0.8

    def test_month_zero_indexed(self):
        """Month should be 0-indexed (0-11)."""
        mixture_df = pd.DataFrame({
            'cell_id': [0],
            'depth_bin': [0],
            'datetime': pd.to_datetime(['2023-01-15 10:00:00']),  # January = month 0
            'epsilon': [1.0],
            'probability': [0.5]
        })

        minimums = build_minimums(mixture_df)

        assert 0 in minimums[0][0]  # January should be 0
        assert isinstance(minimums[0][0][0], list)  # Should be an array
        assert 1 not in minimums[0][0]  # Should not have month 1


class TestBuildReport:
    """Integration tests for build_report function."""

    def test_basic_report_generation(self):
        """Should generate complete report structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal test data
            meta_data = {
                'scenario_id': 'test_scenario_001',
                'description': 'Test scenario'
            }

            model_df = pd.DataFrame({
                '_decision': [1, 1, 2, 2],
                '_choice': ['A', 'B', 'A', 'B'],
                'probability': [0.8, 0.2, 0.7, 0.3]
            })

            reference_df = pd.DataFrame({
                '_decision': [1, 1, 2, 2],
                '_choice': ['A', 'B', 'A', 'B'],
                'probability': [0.5, 0.5, 0.5, 0.5]
            })

            context_df = pd.DataFrame({
                '_decision': [1, 1, 2, 2],
                '_choice': ['A', 'B', 'A', 'B'],
                'datetime': pd.to_datetime(['2023-01-01 10:00', '2023-01-01 10:00',
                                            '2023-01-01 11:00', '2023-01-01 11:00']),
                'h3_index': ['85283473fffffff', '85283473fffffff',
                            '85283473fffffff', '85283473fffffff'],
                'depth_bin': [0, 1, 0, 1]
            })

            model_actuals = pd.DataFrame({
                '_decision': [1, 1],
                '_choice': ['A', 'B'],
                'probability': [0.8, 0.2]
            })

            reference_actuals = pd.DataFrame({
                '_decision': [1, 1],
                '_choice': ['A', 'B'],
                'probability': [0.5, 0.5]
            })

            selections_actuals = pd.DataFrame({
                '_decision': [1],
                '_choice': ['A']
            })

            epsilons = np.array([0.0, 0.5, 1.0])

            # Build report
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

            # Check that all expected files exist
            scenario_dir = os.path.join(tmpdir, 'test_scenario_001')
            assert os.path.exists(scenario_dir)
            assert os.path.exists(os.path.join(scenario_dir, 'meta_data.json'))
            assert os.path.exists(os.path.join(scenario_dir, 'geometries.geojson'))
            assert os.path.exists(os.path.join(scenario_dir, 'cell_depths.json'))
            assert os.path.exists(os.path.join(scenario_dir, 'timestamps.json'))
            assert os.path.exists(os.path.join(scenario_dir, 'minimums.json'))
            assert os.path.exists(os.path.join(scenario_dir, 'support.json'))

            # Check that occupancy file exists
            assert os.path.exists(os.path.join(scenario_dir, '0_occupancy.parquet.gz'))

            # Validate some file contents
            with open(os.path.join(scenario_dir, 'meta_data.json')) as f:
                loaded_meta = json.load(f)
                assert loaded_meta['scenario_id'] == 'test_scenario_001'

            with open(os.path.join(scenario_dir, 'timestamps.json')) as f:
                timestamps = json.load(f)
                assert len(timestamps) == 2

    def test_mismatched_decision_choice_pairs_raises_error(self):
        """Should raise error if model and reference have mismatched pairs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            meta_data = {'scenario_id': 'test'}

            model_df = pd.DataFrame({
                '_decision': [1, 1],
                '_choice': ['A', 'B'],
                'probability': [0.8, 0.2]
            })

            reference_df = pd.DataFrame({
                '_decision': [1, 1],
                '_choice': ['A', 'C'],  # Different choice!
                'probability': [0.5, 0.5]
            })

            context_df = pd.DataFrame({
                '_decision': [1, 1],
                '_choice': ['A', 'B'],
                'datetime': pd.to_datetime(['2023-01-01', '2023-01-01']),
                'h3_index': ['85283473fffffff', '85283473fffffff'],
                'depth_bin': [0, 1]
            })

            with pytest.raises(ValueError, match="same.*pairs"):
                build_report(
                    meta_data, model_df, reference_df, context_df,
                    model_df, reference_df, pd.DataFrame({'_decision': [1], '_choice': ['A']}),
                    np.array([0.5]), tmpdir
                )
