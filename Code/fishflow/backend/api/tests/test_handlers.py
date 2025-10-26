"""
Unit tests for FishFlow API handler functions.

Tests the business logic of each endpoint handler using mocked data access.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import pandas as pd
import numpy as np

from app.depth.handlers import (
    get_scenarios,
    get_scenario,
    get_geometries,
    get_cell_depths,
    get_timestamps,
    get_minimums,
    get_occupancy,
)
from app.depth.models import (
    Scenarios,
    Scenario,
    Geometries,
    CellDepths,
    Timestamps,
    Minimums,
    Occupancy,
)


# Sample test data
SAMPLE_METADATA = {
    "scenario_id": "test_scenario",
    "name": "Test Scenario",
    "species": "Test Fish",
    "model": "test_model",
    "reference_model": "reference_model",
    "region": "test_region",
    "reference_region": "reference_region",
    "description": "A test scenario",
    "time_window": ["2023-01-01 00:00:00", "2023-12-31 23:59:59"],
    "reference_time_window": ["2022-01-01 00:00:00", "2022-12-31 23:59:59"],
    "grid_size": 100,
    "depth_bins": [0.0, 10.0, 20.0, 30.0],
    "resolution": 1000,
    "support": [0.25, 0.50, 0.75],
}

SAMPLE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
            "properties": {"cell_id": 1},
        }
    ],
}

SAMPLE_CELL_DEPTHS = {"1": 30.0, "2": 20.0, "3": 10.0}

SAMPLE_TIMESTAMPS = [
    "2023-01-01 00:00:00",
    "2023-01-01 01:00:00",
    "2023-01-01 02:00:00",
]

SAMPLE_MINIMUMS = {
    "1": {
        "10.0": {
            "1": [0.1] * 24,
            "2": [0.2] * 24,
        }
    }
}


class TestGetScenarios:
    """Tests for get_scenarios handler."""

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.list_directories")
    @patch("app.depth.handlers.read_json_file")
    def test_get_scenarios_success(self, mock_read_json, mock_list_dirs, mock_get_root):
        """Test successful retrieval of all scenarios."""
        mock_get_root.return_value = "/test/data"
        mock_list_dirs.return_value = ["scenario1", "scenario2"]
        mock_read_json.return_value = SAMPLE_METADATA

        result = get_scenarios()

        assert isinstance(result, Scenarios)
        assert len(result.scenarios) == 2
        assert all(isinstance(s, Scenario) for s in result.scenarios)

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.list_directories")
    @patch("app.depth.handlers.read_json_file")
    def test_get_scenarios_skip_corrupted(
        self, mock_read_json, mock_list_dirs, mock_get_root
    ):
        """Test that corrupted scenarios are skipped."""
        mock_get_root.return_value = "/test/data"
        mock_list_dirs.return_value = ["scenario1", "scenario2", "scenario3"]

        # scenario2 is corrupted
        def read_side_effect(root, scenario_id, filename):
            if scenario_id == "scenario2":
                raise HTTPException(status_code=500, detail="Corrupted")
            return SAMPLE_METADATA

        mock_read_json.side_effect = read_side_effect

        result = get_scenarios()

        assert isinstance(result, Scenarios)
        assert len(result.scenarios) == 2  # Only valid scenarios


class TestGetScenario:
    """Tests for get_scenario handler."""

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_scenario_success(self, mock_read_json, mock_get_root):
        """Test successful retrieval of a single scenario."""
        mock_get_root.return_value = "/test/data"
        mock_read_json.return_value = SAMPLE_METADATA

        result = get_scenario("test_scenario")

        assert isinstance(result, Scenario)
        assert result.scenario_id == "test_scenario"
        mock_read_json.assert_called_once_with(
            "/test/data", "test_scenario", "meta_data.json"
        )

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_scenario_not_found(self, mock_read_json, mock_get_root):
        """Test 404 error when scenario doesn't exist."""
        mock_get_root.return_value = "/test/data"
        mock_read_json.side_effect = HTTPException(
            status_code=404, detail="Not found"
        )

        with pytest.raises(HTTPException) as exc_info:
            get_scenario("nonexistent")

        assert exc_info.value.status_code == 404


class TestGetGeometries:
    """Tests for get_geometries handler."""

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_geojson_file")
    def test_get_geometries_success(self, mock_read_geojson, mock_get_root):
        """Test successful retrieval of geometries."""
        mock_get_root.return_value = "/test/data"
        mock_read_geojson.return_value = SAMPLE_GEOJSON

        result = get_geometries("test_scenario")

        assert isinstance(result, Geometries)
        assert result.geojson["type"] == "FeatureCollection"


class TestGetCellDepths:
    """Tests for get_cell_depths handler."""

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_cell_depths_success(self, mock_read_json, mock_get_root):
        """Test successful retrieval of cell depths."""
        mock_get_root.return_value = "/test/data"
        mock_read_json.return_value = {1: 30.0, 2: 20.0}

        result = get_cell_depths("test_scenario")

        assert isinstance(result, CellDepths)
        # Keys should be converted to strings
        assert "1" in result.cell_depths
        assert result.cell_depths["1"] == 30.0


class TestGetTimestamps:
    """Tests for get_timestamps handler."""

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_timestamps_success(self, mock_read_json, mock_get_root):
        """Test successful retrieval of timestamps."""
        mock_get_root.return_value = "/test/data"
        mock_read_json.return_value = SAMPLE_TIMESTAMPS

        result = get_timestamps("test_scenario")

        assert isinstance(result, Timestamps)
        assert len(result.timestamps) == 3

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_timestamps_malformed(self, mock_read_json, mock_get_root):
        """Test error when timestamps.json is not an array."""
        mock_get_root.return_value = "/test/data"
        mock_read_json.return_value = {"invalid": "format"}

        with pytest.raises(HTTPException) as exc_info:
            get_timestamps("test_scenario")

        assert exc_info.value.status_code == 500
        assert "expected array" in exc_info.value.detail


class TestGetMinimums:
    """Tests for get_minimums handler."""

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_minimums_success(self, mock_read_json, mock_get_root):
        """Test successful retrieval of minimums."""
        mock_get_root.return_value = "/test/data"
        mock_read_json.return_value = SAMPLE_MINIMUMS

        result = get_minimums("test_scenario")

        assert isinstance(result, Minimums)
        # Keys should be converted to strings
        assert "1" in result.minimums


class TestGetOccupancy:
    """Tests for get_occupancy handler."""

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    @patch("app.depth.handlers.read_parquet_file")
    def test_get_occupancy_success(
        self, mock_read_parquet, mock_read_json, mock_get_root
    ):
        """Test successful retrieval of occupancy data."""
        mock_get_root.return_value = "/test/data"
        mock_read_json.return_value = SAMPLE_METADATA

        # Create sample parquet data
        # 3 models, 4 depth bins = 12 columns
        # 10 time steps
        num_models = 3
        num_depth_bins = 4
        num_timesteps = 10
        data = np.random.rand(num_timesteps, num_models * num_depth_bins)
        df = pd.DataFrame(data)

        mock_read_parquet.return_value = df

        result = get_occupancy("test_scenario", cell_id=1, depth_bin=10.0)

        assert isinstance(result, Occupancy)
        assert len(result.timelines) == num_models
        assert all(len(timeline) == num_timesteps for timeline in result.timelines)

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_occupancy_missing_cell_id(self, mock_read_json, mock_get_root):
        """Test error when cell_id is missing."""
        mock_get_root.return_value = "/test/data"

        with pytest.raises(HTTPException) as exc_info:
            get_occupancy("test_scenario", cell_id=None, depth_bin=10.0)

        assert exc_info.value.status_code == 400
        assert "cell_id" in exc_info.value.detail

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_occupancy_missing_depth_bin(self, mock_read_json, mock_get_root):
        """Test error when depth_bin is missing."""
        mock_get_root.return_value = "/test/data"

        with pytest.raises(HTTPException) as exc_info:
            get_occupancy("test_scenario", cell_id=1, depth_bin=None)

        assert exc_info.value.status_code == 400
        assert "depth_bin" in exc_info.value.detail

    @patch("app.depth.handlers.get_data_root")
    @patch("app.depth.handlers.read_json_file")
    def test_get_occupancy_invalid_depth_bin(self, mock_read_json, mock_get_root):
        """Test error when depth_bin is not in scenario's depth_bins."""
        mock_get_root.return_value = "/test/data"
        mock_read_json.return_value = SAMPLE_METADATA

        with pytest.raises(HTTPException) as exc_info:
            get_occupancy("test_scenario", cell_id=1, depth_bin=999.0)

        assert exc_info.value.status_code == 400
        assert "not found" in exc_info.value.detail
