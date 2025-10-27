"""Pydantic models for FishFlow depth endpoints.

This module defines the response models for all depth-related API endpoints,
corresponding to the schemas defined in the design documentation.
"""

from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field, RootModel
from datetime import datetime


class Scenario(BaseModel):
    """Model for scenario metadata.

    Corresponds to MetaDataSchema in the design documentation.
    """
    scenario_id: str = Field(..., description="Unique identifier for the scenario")
    name: str = Field(..., description="Human-readable name for the scenario")
    species: str = Field(..., description="Species being modeled")
    model: str = Field(..., description="Model name")
    reference_model: str = Field(..., description="Reference model name")
    region: str = Field(..., description="Geographic region")
    reference_region: str = Field(..., description="Reference geographic region")
    description: str = Field(..., description="Detailed description of the scenario")
    time_window: List[str] = Field(..., description="Time window as [start, end] in 'YYYY-MM-DD HH:MM:SS' format")
    reference_time_window: List[str] = Field(..., description="Reference time window as [start, end] in 'YYYY-MM-DD HH:MM:SS' format")
    grid_size: int = Field(..., description="Size of the grid")
    depth_bins: List[float] = Field(..., description="List of depth bin values")
    resolution: int = Field(..., description="Resolution of the grid")
    support: List[float] = Field(..., description="Support values for models")
    zoom: int = Field(..., description="Map zoom level")
    center: Tuple[float, float] = Field(..., description="Map center as (longitude, latitude)")


class Scenarios(BaseModel):
    """Model for a list of scenarios.

    Used by the /scenarios endpoint to return all available scenarios.
    """
    scenarios: List[Scenario] = Field(..., description="List of available scenarios")


class Geometries(RootModel[Dict[str, Any]]):
    """Model for geometries (GeoJSON).

    Corresponds to GeometriesSchema - a GeoJSON FeatureCollection with cell_id properties.
    Returns GeoJSON directly with top-level keys 'type' and 'features' only.
    """
    root: Dict[str, Any] = Field(..., description="GeoJSON FeatureCollection of polygons with cell_id properties")


class CellDepths(RootModel[Dict[int, float]]):
    """Model for cell depths mapping.

    Corresponds to CellDepthsSchema - maps cell_id to maximum depth bin.
    Returns the dict directly without wrapping: {cell_id(int) -> maximum_depth_bin(float)}
    """
    root: Dict[int, float] = Field(..., description="Mapping of cell_id to maximum_depth_bin")


class Timestamps(BaseModel):
    """Model for timestamps array.

    Corresponds to TimestampsSchema - ordered array of all timestamps in the report.
    """
    timestamps: List[str] = Field(..., description="Ordered list of timestamps")


class Minimums(BaseModel):
    """Model for minimum depth occupancy data.

    Corresponds to MinimumsSchema - nested structure of cell_id -> depth_bin -> month -> hourly minimums.
    """
    minimums: Dict[int, Dict[float, Dict[int, List[float]]]] = Field(
        ...,
        description="Nested mapping: cell_id -> depth_bin -> month -> array[24] of hourly minimums"
    )


class Occupancy(BaseModel):
    """Model for occupancy timelines.

    Corresponds to data from OccupancySchema - timelines for a specific cell and depth bin.
    Returns an array of timelines, one per model.
    """
    timelines: List[List[float]] = Field(
        ...,
        description="Array of timelines (one per model) for the specified cell_id and depth_bin"
    )
