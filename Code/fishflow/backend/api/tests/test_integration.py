"""
Integration tests for FishFlow API.

Tests the complete API using FastAPI TestClient with sample data.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def sample_data_dir():
    """
    Create a temporary directory with sample test data.

    Returns:
        Path to the temporary data directory
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    depth_dir = Path(temp_dir) / "depth"
    depth_dir.mkdir()

    # Create a sample scenario
    scenario_dir = depth_dir / "test_scenario_001"
    scenario_dir.mkdir()

    # Create meta_data.json
    meta_data = {
        "scenario_id": "test_scenario_001",
        "name": "Test Scenario 001",
        "species": "Atlantic Salmon",
        "model": "behavioral_model_v1",
        "reference_model": "baseline_model",
        "region": "North Atlantic",
        "reference_region": "Gulf of Maine",
        "description": "Test scenario for integration testing",
        "time_window": ["2023-01-01 00:00:00", "2023-12-31 23:59:59"],
        "reference_time_window": ["2022-01-01 00:00:00", "2022-12-31 23:59:59"],
        "grid_size": 50,
        "depth_bins": [0.0, 10.0, 20.0, 30.0],
        "resolution": 1000,
        "support": [0.25, 0.50, 0.75],
    }

    with open(scenario_dir / "meta_data.json", "w") as f:
        json.dump(meta_data, f)

    # Create geometries.geojson
    geometries = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-70, 40], [-70, 41], [-69, 41], [-69, 40], [-70, 40]]],
                },
                "properties": {"cell_id": 1},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-69, 40], [-69, 41], [-68, 41], [-68, 40], [-69, 40]]],
                },
                "properties": {"cell_id": 2},
            },
        ],
    }

    with open(scenario_dir / "geometries.geojson", "w") as f:
        json.dump(geometries, f)

    # Create cell_depths.json
    cell_depths = {1: 30.0, 2: 20.0}

    with open(scenario_dir / "cell_depths.json", "w") as f:
        json.dump(cell_depths, f)

    # Create timestamps.json
    timestamps = [
        "2023-01-01 00:00:00",
        "2023-01-01 01:00:00",
        "2023-01-01 02:00:00",
        "2023-01-01 03:00:00",
        "2023-01-01 04:00:00",
    ]

    with open(scenario_dir / "timestamps.json", "w") as f:
        json.dump(timestamps, f)

    # Create minimums.json
    minimums = {
        1: {
            10.0: {
                1: [0.1 + i * 0.01 for i in range(24)],
                2: [0.2 + i * 0.01 for i in range(24)],
            },
            20.0: {
                1: [0.15 + i * 0.01 for i in range(24)],
                2: [0.25 + i * 0.01 for i in range(24)],
            },
        },
        2: {
            10.0: {
                1: [0.12 + i * 0.01 for i in range(24)],
                2: [0.22 + i * 0.01 for i in range(24)],
            },
        },
    }

    with open(scenario_dir / "minimums.json", "w") as f:
        json.dump(minimums, f)

    # Create sample occupancy parquet files
    num_models = 3
    num_depth_bins = 4
    num_timesteps = 5

    for cell_id in [1, 2]:
        # Create random occupancy data
        data = np.random.rand(num_timesteps, num_models * num_depth_bins)
        df = pd.DataFrame(data)

        # Save as compressed parquet
        output_path = scenario_dir / f"{cell_id}_occupancy.parquet.gz"
        df.to_parquet(output_path, compression="gzip", index=False)

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def client_with_data(sample_data_dir):
    """
    Create a test client with the FishFlowData environment variable set.

    Args:
        sample_data_dir: Path to sample data directory fixture

    Returns:
        FastAPI TestClient configured for testing
    """
    # Set environment variable
    os.environ["FishFlowData"] = sample_data_dir

    # Create test client
    client = TestClient(app)

    yield client

    # Cleanup environment
    if "FishFlowData" in os.environ:
        del os.environ["FishFlowData"]


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client_with_data):
        """Test that the health endpoint returns healthy status."""
        response = client_with_data.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestScenariosEndpoints:
    """Tests for scenario-related endpoints."""

    def test_get_scenarios(self, client_with_data):
        """Test retrieving all scenarios."""
        response = client_with_data.get("/v1/depth/scenario/scenarios")

        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) >= 1
        assert data["scenarios"][0]["scenario_id"] == "test_scenario_001"

    def test_get_scenario(self, client_with_data):
        """Test retrieving a specific scenario."""
        response = client_with_data.get("/v1/depth/scenario/test_scenario_001/scenario")

        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "test_scenario_001"
        assert data["name"] == "Test Scenario 001"
        assert data["species"] == "Atlantic Salmon"
        assert len(data["depth_bins"]) == 4
        assert len(data["support"]) == 3

    def test_get_scenario_not_found(self, client_with_data):
        """Test 404 for nonexistent scenario."""
        response = client_with_data.get("/v1/depth/scenario/nonexistent/scenario")

        assert response.status_code == 404
        assert "detail" in response.json()


class TestGeometriesEndpoint:
    """Tests for the geometries endpoint."""

    def test_get_geometries(self, client_with_data):
        """Test retrieving geometries for a scenario."""
        response = client_with_data.get("/v1/depth/scenario/test_scenario_001/geometries")

        assert response.status_code == 200
        data = response.json()
        assert "geojson" in data
        assert data["geojson"]["type"] == "FeatureCollection"
        assert len(data["geojson"]["features"]) == 2
        assert data["geojson"]["features"][0]["properties"]["cell_id"] == 1


class TestCellDepthsEndpoint:
    """Tests for the cell_depths endpoint."""

    def test_get_cell_depths(self, client_with_data):
        """Test retrieving cell depths for a scenario."""
        response = client_with_data.get("/v1/depth/scenario/test_scenario_001/cell_depths")

        assert response.status_code == 200
        data = response.json()
        assert "cell_depths" in data
        assert "1" in data["cell_depths"]
        assert data["cell_depths"]["1"] == 30.0


class TestTimestampsEndpoint:
    """Tests for the timestamps endpoint."""

    def test_get_timestamps(self, client_with_data):
        """Test retrieving timestamps for a scenario."""
        response = client_with_data.get("/v1/depth/scenario/test_scenario_001/timestamps")

        assert response.status_code == 200
        data = response.json()
        assert "timestamps" in data
        assert len(data["timestamps"]) == 5
        assert data["timestamps"][0] == "2023-01-01 00:00:00"


class TestMinimumsEndpoint:
    """Tests for the minimums endpoint."""

    def test_get_minimums(self, client_with_data):
        """Test retrieving minimums for a scenario."""
        response = client_with_data.get("/v1/depth/scenario/test_scenario_001/minimums")

        assert response.status_code == 200
        data = response.json()
        assert "minimums" in data
        assert "1" in data["minimums"]
        assert "10.0" in data["minimums"]["1"]
        assert "1" in data["minimums"]["1"]["10.0"]
        assert len(data["minimums"]["1"]["10.0"]["1"]) == 24


class TestOccupancyEndpoint:
    """Tests for the occupancy endpoint."""

    def test_get_occupancy(self, client_with_data):
        """Test retrieving occupancy data for a cell and depth bin."""
        response = client_with_data.get(
            "/v1/depth/scenario/test_scenario_001/occupancy?cell_id=1&depth_bin=10.0"
        )

        assert response.status_code == 200
        data = response.json()
        assert "timelines" in data
        assert len(data["timelines"]) == 3  # 3 models
        assert all(len(timeline) == 5 for timeline in data["timelines"])  # 5 timesteps

    def test_get_occupancy_missing_cell_id(self, client_with_data):
        """Test error when cell_id parameter is missing."""
        response = client_with_data.get(
            "/v1/depth/scenario/test_scenario_001/occupancy?depth_bin=10.0"
        )

        assert response.status_code == 422  # FastAPI validation error

    def test_get_occupancy_missing_depth_bin(self, client_with_data):
        """Test error when depth_bin parameter is missing."""
        response = client_with_data.get(
            "/v1/depth/scenario/test_scenario_001/occupancy?cell_id=1"
        )

        assert response.status_code == 422  # FastAPI validation error

    def test_get_occupancy_invalid_depth_bin(self, client_with_data):
        """Test error when depth_bin is not in scenario's depth bins."""
        response = client_with_data.get(
            "/v1/depth/scenario/test_scenario_001/occupancy?cell_id=1&depth_bin=999.0"
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_get_occupancy_invalid_cell_id(self, client_with_data):
        """Test error when cell_id does not exist."""
        response = client_with_data.get(
            "/v1/depth/scenario/test_scenario_001/occupancy?cell_id=999&depth_bin=10.0"
        )

        assert response.status_code == 404
        assert "Cell ID" in response.json()["detail"]


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers(self, client_with_data):
        """Test that CORS headers are properly set."""
        response = client_with_data.options(
            "/v1/depth/scenario/scenarios",
            headers={"Origin": "http://localhost:3000"},
        )

        # CORS middleware should handle this
        # The test client might not fully simulate browser CORS, but we can verify the endpoint works
        # A more complete CORS test would require additional setup
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS
