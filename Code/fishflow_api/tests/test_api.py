"""Integration tests for FishFlow API endpoints."""

import pytest
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
from app.main import app


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a complete test data directory structure."""
    depth_dir = tmp_path / "depth"
    depth_dir.mkdir()

    scenario_id = "test_scenario_1"
    scenario_dir = depth_dir / scenario_id
    scenario_dir.mkdir()

    # Create metadata
    metadata = {
        "scenario_id": scenario_id,
        "name": "Test Scenario",
        "species": "Test Species",
        "model": "Test Model",
        "reference_model": "Reference Model",
        "region": "Test Region",
        "reference_region": "Reference Region",
        "description": "A test scenario",
        "time_window": ["2024-01-01 00:00:00", "2024-01-31 23:59:59"],
        "reference_time_window": ["2023-01-01 00:00:00", "2023-01-31 23:59:59"],
        "grid_size": 100,
        "depth_bins": [0.0, 10.0, 20.0, 30.0],
        "resolution": 1000,
        "support": [0.5, 0.3, 0.2],
        "zoom": 8,
        "center": [-122.4194, 37.7749]
    }
    with open(scenario_dir / "meta_data.json", 'w') as f:
        json.dump(metadata, f)

    # Create geometries (simple GeoJSON)
    geometries = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"cell_id": 1},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-122.5, 37.7], [-122.4, 37.7], [-122.4, 37.8], [-122.5, 37.8], [-122.5, 37.7]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"cell_id": 2},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-122.4, 37.7], [-122.3, 37.7], [-122.3, 37.8], [-122.4, 37.8], [-122.4, 37.7]]]
                }
            }
        ]
    }
    with open(scenario_dir / "geometries.geojson", 'w') as f:
        json.dump(geometries, f)

    # Create cell_depths
    cell_depths = {
        "1": 30.0,
        "2": 20.0
    }
    with open(scenario_dir / "cell_depths.json", 'w') as f:
        json.dump(cell_depths, f)

    # Create timestamps
    timestamps = [
        "2024-01-01 00:00:00",
        "2024-01-01 01:00:00",
        "2024-01-01 02:00:00"
    ]
    with open(scenario_dir / "timestamps.json", 'w') as f:
        json.dump(timestamps, f)

    # Create minimums
    minimums = {
        "1": {
            "10.0": {
                "1": [0.1] * 24,
                "2": [0.2] * 24
            }
        },
        "2": {
            "10.0": {
                "1": [0.15] * 24
            }
        }
    }
    with open(scenario_dir / "minimums.json", 'w') as f:
        json.dump(minimums, f)

    # Create occupancy parquet file for cell 1
    # 3 timestamps x (3 models x 4 depth_bins) = 3 rows x 12 columns
    num_timestamps = 3
    num_models = 3
    num_depth_bins = 4
    data = np.random.rand(num_timestamps, num_models * num_depth_bins)
    df = pd.DataFrame(data)
    df.to_parquet(scenario_dir / "1_occupancy.parquet.gz", compression='gzip')

    # Create occupancy parquet file for cell 2
    df2 = pd.DataFrame(np.random.rand(num_timestamps, num_models * num_depth_bins))
    df2.to_parquet(scenario_dir / "2_occupancy.parquet.gz", compression='gzip')

    return tmp_path


@pytest.fixture
def client(test_data_dir):
    """Create a test client with the test data directory."""
    os.environ["FISHFLOW_DATA_DIR"] = str(test_data_dir)
    return TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test that health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestScenariosEndpoint:
    """Test scenarios listing endpoint."""

    def test_get_scenarios(self, client):
        """Test getting all scenarios."""
        response = client.get("/v1/depth/scenario/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) == 1
        assert data["scenarios"][0]["scenario_id"] == "test_scenario_1"
        assert data["scenarios"][0]["name"] == "Test Scenario"


class TestScenarioEndpoint:
    """Test individual scenario metadata endpoint."""

    def test_get_scenario(self, client):
        """Test getting scenario metadata."""
        response = client.get("/v1/depth/scenario/test_scenario_1/scenario")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "test_scenario_1"
        assert data["name"] == "Test Scenario"
        assert data["species"] == "Test Species"
        assert len(data["depth_bins"]) == 4

    def test_get_scenario_not_found(self, client):
        """Test getting non-existent scenario."""
        response = client.get("/v1/depth/scenario/nonexistent/scenario")
        assert response.status_code == 404


class TestGeometriesEndpoint:
    """Test geometries endpoint."""

    def test_get_geometries(self, client):
        """Test getting geometries.

        The endpoint should return GeoJSON directly with only 'type' and 'features'
        at the top level, as specified in the design document.
        """
        response = client.get("/v1/depth/scenario/test_scenario_1/geometries")
        assert response.status_code == 200
        data = response.json()
        # Response should be GeoJSON directly, not wrapped in {"geojson": ...}
        assert "type" in data
        assert "features" in data
        # Only 'type' and 'features' should be present at top level
        assert set(data.keys()) == {"type", "features"}
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2


class TestCellDepthsEndpoint:
    """Test cell depths endpoint."""

    def test_get_cell_depths(self, client):
        """Test getting cell depths."""
        response = client.get("/v1/depth/scenario/test_scenario_1/cell_depths")
        assert response.status_code == 200
        data = response.json()
        # Cell depths should be unwrapped: {cell_id(int) -> maximum_depth_bin(float)}
        assert "1" in data
        assert data["1"] == 30.0
        assert data["2"] == 20.0


class TestTimestampsEndpoint:
    """Test timestamps endpoint."""

    def test_get_timestamps(self, client):
        """Test getting timestamps.

        The endpoint should return an unwrapped array of timestamps directly,
        as specified in the design document.
        """
        response = client.get("/v1/depth/scenario/test_scenario_1/timestamps")
        assert response.status_code == 200
        data = response.json()
        # Response should be an array directly, not wrapped in {"timestamps": ...}
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0] == "2024-01-01 00:00:00"


class TestMinimumsEndpoint:
    """Test minimums endpoint."""

    def test_get_minimums(self, client):
        """Test getting minimums.

        The endpoint should return an unwrapped nested dict directly,
        as specified in the design document:
        {cell_id(int) -> {depth_bin -> {month(int) -> minimums_array}}}
        """
        response = client.get("/v1/depth/scenario/test_scenario_1/minimums")
        assert response.status_code == 200
        data = response.json()
        # Response should be the nested dict directly, not wrapped in {"minimums": ...}
        assert isinstance(data, dict)
        assert "1" in data
        assert "10.0" in data["1"]
        assert "1" in data["1"]["10.0"]
        # minimums_array should be length 24 (hourly data 0-23)
        assert len(data["1"]["10.0"]["1"]) == 24


class TestOccupancyEndpoint:
    """Test occupancy endpoint."""

    def test_get_occupancy(self, client):
        """Test getting occupancy timelines."""
        response = client.get(
            "/v1/depth/scenario/test_scenario_1/occupancy",
            params={"cell_id": 1, "depth_bin": 10.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert "timelines" in data
        # Should have 3 models (from support in metadata)
        assert len(data["timelines"]) == 3
        # Each timeline should have 3 timestamps
        for timeline in data["timelines"]:
            assert len(timeline) == 3

    def test_get_occupancy_invalid_depth_bin(self, client):
        """Test getting occupancy with invalid depth bin."""
        response = client.get(
            "/v1/depth/scenario/test_scenario_1/occupancy",
            params={"cell_id": 1, "depth_bin": 99.0}
        )
        assert response.status_code == 400

    def test_get_occupancy_missing_params(self, client):
        """Test getting occupancy without required parameters."""
        response = client.get("/v1/depth/scenario/test_scenario_1/occupancy")
        assert response.status_code == 422  # Validation error


class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_missing_env_var(self, client):
        """Test behavior when FISHFLOW_DATA_DIR is not set."""
        # Remove the environment variable
        original = os.environ.get("FISHFLOW_DATA_DIR")
        if "FISHFLOW_DATA_DIR" in os.environ:
            del os.environ["FISHFLOW_DATA_DIR"]

        response = client.get("/v1/depth/scenario/scenarios")
        assert response.status_code == 500

        # Restore environment variable
        if original:
            os.environ["FISHFLOW_DATA_DIR"] = original
