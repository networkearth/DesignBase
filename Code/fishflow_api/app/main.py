"""Main FastAPI application for FishFlow API.

This module sets up the FastAPI application and registers all endpoints.
"""

import os
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from app.depth.models import (
    Scenarios,
    Scenario,
    Geometries,
    CellDepths,
    Timestamps,
    Minimums,
    Occupancy
)
from app.depth.handlers import (
    get_scenarios,
    get_scenario,
    get_geometries,
    get_cell_depths,
    get_timestamps,
    get_minimums,
    get_occupancy
)


# Initialize FastAPI app
app = FastAPI(
    title="FishFlow API",
    description="API serving data from behavioral models for the FishFlow App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint.

    Returns:
        200 OK if the API is up and running
    """
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "message": "FishFlow API is running"}
    )


@app.get("/v1/depth/scenario/scenarios", response_model=Scenarios, tags=["Depth"])
async def list_scenarios():
    """Get all available scenarios.

    Returns:
        Scenarios: List of all scenarios with their metadata
    """
    return get_scenarios()


@app.get("/v1/depth/scenario/{scenario_id}/scenario", response_model=Scenario, tags=["Depth"])
async def get_scenario_metadata(scenario_id: str):
    """Get metadata for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Scenario: Metadata for the requested scenario
    """
    return get_scenario(scenario_id)


@app.get("/v1/depth/scenario/{scenario_id}/geometries", response_model=Geometries, tags=["Depth"])
async def get_scenario_geometries(scenario_id: str):
    """Get geometries (GeoJSON) for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Geometries: GeoJSON FeatureCollection with cell geometries
    """
    return get_geometries(scenario_id)


@app.get("/v1/depth/scenario/{scenario_id}/cell_depths", response_model=CellDepths, tags=["Depth"])
async def get_scenario_cell_depths(scenario_id: str):
    """Get cell depths mapping for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        CellDepths: Mapping of cell_id to maximum depth bin
    """
    return get_cell_depths(scenario_id)


@app.get("/v1/depth/scenario/{scenario_id}/timestamps", response_model=Timestamps, tags=["Depth"])
async def get_scenario_timestamps(scenario_id: str):
    """Get timestamps array for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Timestamps: Ordered list of all timestamps in the report
    """
    return get_timestamps(scenario_id)


@app.get("/v1/depth/scenario/{scenario_id}/minimums", response_model=Minimums, tags=["Depth"])
async def get_scenario_minimums(scenario_id: str):
    """Get minimum depth occupancy data for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Minimums: Nested structure of minimum occupancy by cell, depth, month, and hour
    """
    return get_minimums(scenario_id)


@app.get("/v1/depth/scenario/{scenario_id}/occupancy", response_model=Occupancy, tags=["Depth"])
async def get_scenario_occupancy(
    scenario_id: str,
    cell_id: int = Query(..., description="Cell identifier"),
    depth_bin: float = Query(..., description="Depth bin value")
):
    """Get occupancy timelines for a specific cell and depth bin.

    Args:
        scenario_id: Unique identifier for the scenario
        cell_id: Cell identifier
        depth_bin: Depth bin value (must match a value in metadata depth_bins)

    Returns:
        Occupancy: Array of timelines, one per model, for the specified cell and depth bin
    """
    return get_occupancy(scenario_id, cell_id, depth_bin)


if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    mode = os.getenv("FISHFLOW_API_MODE", "DEV")
    host = "0.0.0.0" if mode == "PROD" else "127.0.0.1"

    uvicorn.run(app, host=host, port=8000, reload=(mode == "DEV"))
