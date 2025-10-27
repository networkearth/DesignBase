"""
Unit tests for fishflow.depth.report module.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import os
import json
from datetime import datetime
from fishflow.depth.report import (
    build_cell_depths,
    build_minimums,
    build_occupancy,
    build_report,
)


class TestBuildCellDepths:
    """Tests for build_cell_depths function."""

    def test_basic_depths(self):
        """Test basic cell depth computation."""
        context_df = pd.DataFrame(
            {
                "cell_id": [0, 0, 1, 1, 1],
                "depth_bin": [10.0, 20.0, 15.0, 25.0, 30.0],
            }
        )

        cell_depths = build_cell_depths(context_df)

        # Check max depths per cell
        assert cell_depths[0] == 20.0
        assert cell_depths[1] == 30.0

    def test_single_depth(self):
        """Test cell with single depth."""
        context_df = pd.DataFrame(
            {
                "cell_id": [0],
                "depth_bin": [10.0],
            }
        )

        cell_depths = build_cell_depths(context_df)

        assert cell_depths[0] == 10.0

    def test_missing_columns(self):
        """Test that missing columns raise error."""
        context_df = pd.DataFrame(
            {
                "cell_id": [0, 1],
            }
        )

        with pytest.raises(ValueError, match="must contain columns"):
            build_cell_depths(context_df)


class TestBuildMinimums:
    """Tests for build_minimums function."""

    def test_basic_minimums(self):
        """Test basic minimums computation."""
        mixture_df = pd.DataFrame(
            {
                "cell_id": [0, 0, 0, 0],
                "depth_bin": [10.0, 10.0, 10.0, 10.0],
                "datetime": [
                    datetime(2024, 1, 1, 10, 0, 0),
                    datetime(2024, 1, 1, 10, 30, 0),
                    datetime(2024, 1, 1, 11, 0, 0),
                    datetime(2024, 1, 2, 10, 0, 0),
                ],
                "probability": [0.5, 0.3, 0.4, 0.6],
                "epsilon": [1.0, 1.0, 1.0, 1.0],
            }
        )

        minimums = build_minimums(mixture_df)

        # Check structure
        assert 0 in minimums
        assert 10.0 in minimums[0]
        assert 1 in minimums[0][10.0]  # January
        assert len(minimums[0][10.0][1]) == 24  # 24 hours

        # Check that hour 10 has minimum of 0.3 (from two entries at hour 10)
        assert minimums[0][10.0][1][10] == 0.3

        # Check that hour 11 has value 0.4
        assert minimums[0][10.0][1][11] == 0.4

    def test_epsilon_filtering(self):
        """Test that only epsilon=1 is used."""
        mixture_df = pd.DataFrame(
            {
                "cell_id": [0, 0],
                "depth_bin": [10.0, 10.0],
                "datetime": [
                    datetime(2024, 1, 1, 10, 0, 0),
                    datetime(2024, 1, 1, 10, 0, 0),
                ],
                "probability": [0.3, 0.7],
                "epsilon": [1.0, 0.0],
            }
        )

        minimums = build_minimums(mixture_df)

        # Should only use epsilon=1.0 value (0.3)
        assert minimums[0][10.0][1][10] == 0.3

    def test_updating_existing_minimums(self):
        """Test updating existing minimums dictionary."""
        existing = {
            0: {10.0: {1: [0.5] + [None] * 23}}
        }

        mixture_df = pd.DataFrame(
            {
                "cell_id": [0],
                "depth_bin": [10.0],
                "datetime": [datetime(2024, 1, 1, 0, 0, 0)],
                "probability": [0.3],
                "epsilon": [1.0],
            }
        )

        minimums = build_minimums(mixture_df, existing)

        # Should update with new minimum
        assert minimums[0][10.0][1][0] == 0.3


class TestBuildOccupancy:
    """Tests for build_occupancy function."""

    def test_basic_occupancy(self):
        """Test basic occupancy dataframe construction."""
        dates = [datetime(2024, 1, 1, i, 0, 0) for i in range(3)]

        mixture_df = pd.DataFrame(
            {
                "depth_bin": [10.0, 10.0, 10.0, 20.0, 20.0, 20.0],
                "datetime": dates + dates,
                "probability": [0.6, 0.7, 0.8, 0.4, 0.3, 0.2],
                "epsilon": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            }
        )

        occupancy_df = build_occupancy(mixture_df)

        # Check shape: 3 times × 2 depth bins × 1 epsilon = 2 columns
        assert occupancy_df.shape[0] == 3
        assert occupancy_df.shape[1] == 2

        # Check that values are present
        assert not occupancy_df.isnull().all().all()

    def test_multiple_epsilons(self):
        """Test with multiple epsilon values."""
        dates = [datetime(2024, 1, 1, 0, 0, 0)]

        mixture_df = pd.DataFrame(
            {
                "depth_bin": [10.0, 10.0, 20.0, 20.0],
                "datetime": dates * 4,
                "probability": [0.6, 0.5, 0.4, 0.5],
                "epsilon": [0.0, 1.0, 0.0, 1.0],
            }
        )

        occupancy_df = build_occupancy(mixture_df)

        # Check shape: 1 time × 2 depth bins × 2 epsilons = 4 columns
        assert occupancy_df.shape[0] == 1
        assert occupancy_df.shape[1] == 4

        # Verify column indexing: model_idx = col // num_depth_bins
        # Column 0: epsilon=0.0, depth=10.0
        # Column 1: epsilon=0.0, depth=20.0
        # Column 2: epsilon=1.0, depth=10.0
        # Column 3: epsilon=1.0, depth=20.0
        assert occupancy_df.iloc[0, 0] == 0.6  # epsilon=0, depth=10
        assert occupancy_df.iloc[0, 1] == 0.4  # epsilon=0, depth=20
        assert occupancy_df.iloc[0, 2] == 0.5  # epsilon=1, depth=10
        assert occupancy_df.iloc[0, 3] == 0.5  # epsilon=1, depth=20


class TestBuildReport:
    """Integration tests for build_report function."""

    def test_complete_report(self):
        """Test complete report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test data
            h3_index = "85283473fffffff"
            dates = [
                datetime(2024, 1, 1, i, 0, 0) for i in range(3)
            ]

            # Model predictions
            model_df = pd.DataFrame(
                {
                    "_decision": [1, 1, 2, 2, 3, 3],
                    "_choice": ["A", "B", "A", "B", "A", "B"],
                    "probability": [0.7, 0.3, 0.8, 0.2, 0.6, 0.4],
                }
            )

            reference_model_df = pd.DataFrame(
                {
                    "_decision": [1, 1, 2, 2, 3, 3],
                    "_choice": ["A", "B", "A", "B", "A", "B"],
                    "probability": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                }
            )

            context_df = pd.DataFrame(
                {
                    "_decision": [1, 1, 2, 2, 3, 3],
                    "_choice": ["A", "B", "A", "B", "A", "B"],
                    "datetime": dates + dates,
                    "h3_index": [h3_index] * 6,
                    "depth_bin": [10.0, 20.0, 10.0, 20.0, 10.0, 20.0],
                }
            )

            # Actuals data
            model_actuals_df = model_df.copy()
            reference_model_actuals_df = reference_model_df.copy()
            selections_actuals_df = pd.DataFrame(
                {
                    "_decision": [1, 2, 3],
                    "_choice": ["A", "A", "B"],
                }
            )

            epsilons = np.array([0.0, 0.5, 1.0])

            meta_data = {
                "scenario_id": "test_scenario",
                "name": "Test Scenario",
                "species": "Test Fish",
                "model": "Test Model",
                "reference_model": "Uniform Model",
                "region": "Test Region",
                "reference_region": "Test Reference Region",
                "description": "A test scenario",
                "reference_time_window": [
                    "2024-01-01 00:00:00",
                    "2024-01-31 23:59:59",
                ],
                "zoom": 5,
                "center": (-70.0, 42.0),
            }

            # Build report
            build_report(
                meta_data,
                model_df,
                reference_model_df,
                context_df,
                model_actuals_df,
                reference_model_actuals_df,
                selections_actuals_df,
                epsilons,
                tmpdir,
            )

            # Check that all files were created
            scenario_dir = os.path.join(tmpdir, "test_scenario")
            assert os.path.exists(scenario_dir)
            assert os.path.exists(os.path.join(scenario_dir, "meta_data.json"))
            assert os.path.exists(os.path.join(scenario_dir, "geometries.geojson"))
            assert os.path.exists(os.path.join(scenario_dir, "timestamps.json"))
            assert os.path.exists(os.path.join(scenario_dir, "cell_depths.json"))
            assert os.path.exists(os.path.join(scenario_dir, "minimums.json"))
            assert os.path.exists(os.path.join(scenario_dir, "0_occupancy.parquet.gz"))

            # Check metadata content
            with open(os.path.join(scenario_dir, "meta_data.json")) as f:
                saved_meta = json.load(f)

            assert saved_meta["scenario_id"] == "test_scenario"
            assert "resolution" in saved_meta
            assert "grid_size" in saved_meta
            assert "depth_bins" in saved_meta
            assert "support" in saved_meta
            assert "time_window" in saved_meta

            # Check that support is valid
            support = np.array(saved_meta["support"])
            assert len(support) == len(epsilons)
            assert np.all(support >= 0)
            assert np.all(support <= 1)
            assert np.isclose(support.sum(), 1.0)

    def test_missing_metadata(self):
        """Test that missing metadata raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            meta_data = {
                "scenario_id": "test",
                "name": "Test",
                # Missing other required fields
            }

            model_df = pd.DataFrame(
                {
                    "_decision": [1],
                    "_choice": ["A"],
                    "probability": [1.0],
                }
            )

            with pytest.raises(ValueError, match="missing required fields"):
                build_report(
                    meta_data,
                    model_df,
                    model_df,
                    model_df,
                    model_df,
                    model_df,
                    pd.DataFrame({"_decision": [1], "_choice": ["A"]}),
                    np.array([0.5]),
                    tmpdir,
                )
