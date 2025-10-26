"""
Pydantic models for FishFlow depth API endpoints.

These models define the response schemas for the depth-related endpoints,
corresponding to the data structures defined in the API specification.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Scenario(BaseModel):
    """
    Model for scenario metadata.

    Corresponds to MetaDataSchema from the API specification.

    Attributes:
        scenario_id: Unique identifier for the scenario
        name: Human-readable name of the scenario
        species: Species being modeled
        model: Model type used for predictions
        reference_model: Reference model for comparison
        region: Geographic region of the scenario
        reference_region: Reference region for comparison
        description: Detailed description of the scenario
        time_window: Time range for the scenario [start, end] in "YYYY-MM-DD HH:MM:SS" format
        reference_time_window: Reference time range [start, end] in "YYYY-MM-DD HH:MM:SS" format
        grid_size: Size of the spatial grid
        depth_bins: List of depth values defining the bins
        resolution: Spatial resolution in meters
        support: Model support values
    """
    scenario_id: str
    name: str
    species: str
    model: str
    reference_model: str
    region: str
    reference_region: str
    description: str
    time_window: List[str] = Field(..., min_length=2, max_length=2)
    reference_time_window: List[str] = Field(..., min_length=2, max_length=2)
    grid_size: int
    depth_bins: List[float]
    resolution: int
    support: List[float]


class Scenarios(BaseModel):
    """
    Model for a list of scenarios.

    Attributes:
        scenarios: List of Scenario objects containing metadata for each scenario
    """
    scenarios: List[Scenario]


class Geometries(BaseModel):
    """
    Model for GeoJSON geometries.

    Corresponds to GeometriesSchema from the API specification.
    Contains GeoJSON polygons with cell_id properties.

    Attributes:
        geojson: GeoJSON object containing polygons with cell_id properties
    """
    geojson: Dict[str, Any] = Field(..., description="GeoJSON FeatureCollection with cell_id properties")


class CellDepths(BaseModel):
    """
    Model for cell depth mappings.

    Corresponds to CellDepthsSchema from the API specification.
    Maps cell IDs to their maximum depth bins.

    Attributes:
        cell_depths: Dictionary mapping cell_id (as string) to maximum_depth_bin (float)
    """
    cell_depths: Dict[str, float] = Field(..., description="Mapping of cell_id to maximum_depth_bin")


class Timestamps(BaseModel):
    """
    Model for ordered timestamps.

    Corresponds to TimestampsSchema from the API specification.

    Attributes:
        timestamps: Ordered array of all timestamps in the report
    """
    timestamps: List[str] = Field(..., description="Ordered list of timestamps")


class Minimums(BaseModel):
    """
    Model for minimum depth occupancy data.

    Corresponds to MinimumsSchema from the API specification.
    Structure: {cell_id -> {depth_bin -> {month -> minimums_array}}}
    where minimums_array contains 24 hourly minimum values.

    Attributes:
        minimums: Nested dictionary containing minimum occupancy values
    """
    minimums: Dict[str, Dict[str, Dict[str, List[float]]]] = Field(
        ...,
        description="Mapping of cell_id -> depth_bin -> month -> hourly minimums (24 values)"
    )


class Occupancy(BaseModel):
    """
    Model for occupancy timeline data.

    Corresponds to a subset of OccupancySchema from the API specification.
    Contains timelines for multiple models at a specific cell and depth bin.

    Attributes:
        timelines: Array of likelihood timelines, one per model
    """
    timelines: List[List[Optional[float]]] = Field(
        ...,
        description="Array of timelines, one per model. Each timeline is an array of likelihood values (or null)"
    )
