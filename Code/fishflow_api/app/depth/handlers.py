"""Handler functions for FishFlow depth endpoints.

This module implements all the business logic for depth-related API endpoints,
including data retrieval and transformation from the report files.
"""

import os
from typing import List
from fastapi import HTTPException
from app.depth.models import (
    Scenario,
    Scenarios,
    Geometries,
    CellDepths,
    Timestamps,
    Minimums,
    Occupancy
)
from app.data_loader import (
    read_json_file,
    read_geojson_file,
    read_parquet_file,
    list_directories
)


def get_data_dir() -> str:
    """Get the data directory from environment variable.

    Returns:
        Data directory path (local or S3)

    Raises:
        HTTPException: If FISHFLOW_DATA_DIR is not set
    """
    data_dir = os.getenv("FISHFLOW_DATA_DIR")
    if not data_dir:
        raise HTTPException(
            status_code=500,
            detail="FISHFLOW_DATA_DIR environment variable not set"
        )
    return data_dir


def get_scenarios() -> Scenarios:
    """Get all available scenarios.

    Loops through the /depth directory and retrieves metadata for each scenario.

    Returns:
        Scenarios model containing list of all scenarios

    Raises:
        HTTPException: For file system errors or corrupt data
    """
    try:
        data_dir = get_data_dir()
        depth_dir = "depth"

        # List all scenario directories
        scenario_dirs = list_directories(data_dir, depth_dir)

        if not scenario_dirs:
            raise HTTPException(
                status_code=404,
                detail="No scenarios found in depth directory"
            )

        scenarios_list = []
        for scenario_id in scenario_dirs:
            try:
                # Read metadata for each scenario
                meta_path = f"{depth_dir}/{scenario_id}/meta_data.json"
                meta_data = read_json_file(data_dir, meta_path)
                scenarios_list.append(Scenario(**meta_data))
            except FileNotFoundError:
                # Skip scenarios without metadata
                continue
            except Exception as e:
                # Log but continue for individual scenario errors
                print(f"Warning: Could not load scenario {scenario_id}: {e}")
                continue

        if not scenarios_list:
            raise HTTPException(
                status_code=404,
                detail="No valid scenarios found with metadata"
            )

        return Scenarios(scenarios=scenarios_list)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading scenarios: {str(e)}"
        )


def get_scenario(scenario_id: str) -> Scenario:
    """Get metadata for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Scenario model with metadata

    Raises:
        HTTPException: If scenario not found or data is corrupt
    """
    try:
        data_dir = get_data_dir()
        meta_path = f"depth/{scenario_id}/meta_data.json"

        meta_data = read_json_file(data_dir, meta_path)
        return Scenario(**meta_data)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario '{scenario_id}' not found"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Corrupt metadata for scenario '{scenario_id}': {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading scenario '{scenario_id}': {str(e)}"
        )


def get_geometries(scenario_id: str) -> Geometries:
    """Get geometries (GeoJSON) for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Geometries model with GeoJSON data (returns GeoJSON directly with only 'type' and 'features' keys)

    Raises:
        HTTPException: If scenario not found or data is corrupt
    """
    try:
        data_dir = get_data_dir()
        geojson_path = f"depth/{scenario_id}/geometries.geojson"

        geojson_data = read_geojson_file(data_dir, geojson_path)

        # Ensure only 'type' and 'features' keys are present at top level
        # as specified in the design document
        if not isinstance(geojson_data, dict):
            raise ValueError("GeoJSON must be a dictionary")

        if 'type' not in geojson_data or 'features' not in geojson_data:
            raise ValueError("GeoJSON must contain 'type' and 'features' keys")

        # Return only the essential GeoJSON structure
        clean_geojson = {
            'type': geojson_data['type'],
            'features': geojson_data['features']
        }

        return Geometries(clean_geojson)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Geometries not found for scenario '{scenario_id}'"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Corrupt geometries data for scenario '{scenario_id}': {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading geometries for scenario '{scenario_id}': {str(e)}"
        )


def get_cell_depths(scenario_id: str) -> CellDepths:
    """Get cell depths mapping for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        CellDepths model with cell_id to max depth mapping (unwrapped dict)

    Raises:
        HTTPException: If scenario not found or data is corrupt
    """
    try:
        data_dir = get_data_dir()
        cell_depths_path = f"depth/{scenario_id}/cell_depths.json"

        cell_depths_data = read_json_file(data_dir, cell_depths_path)

        # Convert string keys to integers
        cell_depths_int = {int(k): v for k, v in cell_depths_data.items()}

        return CellDepths(cell_depths_int)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Cell depths not found for scenario '{scenario_id}'"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Corrupt cell depths data for scenario '{scenario_id}': {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading cell depths for scenario '{scenario_id}': {str(e)}"
        )


def get_timestamps(scenario_id: str) -> Timestamps:
    """Get timestamps array for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Timestamps model with ordered list of timestamps (unwrapped array)

    Raises:
        HTTPException: If scenario not found or data is corrupt
    """
    try:
        data_dir = get_data_dir()
        timestamps_path = f"depth/{scenario_id}/timestamps.json"

        timestamps_data = read_json_file(data_dir, timestamps_path)

        if not isinstance(timestamps_data, list):
            raise ValueError("Timestamps data must be a list")

        return Timestamps(timestamps_data)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Timestamps not found for scenario '{scenario_id}'"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Corrupt timestamps data for scenario '{scenario_id}': {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading timestamps for scenario '{scenario_id}': {str(e)}"
        )


def get_minimums(scenario_id: str) -> Minimums:
    """Get minimum depth occupancy data for a specific scenario.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Minimums model with nested cell/depth/month/hourly data (unwrapped dict)

    Raises:
        HTTPException: If scenario not found or data is corrupt
    """
    try:
        data_dir = get_data_dir()
        minimums_path = f"depth/{scenario_id}/minimums.json"

        minimums_data = read_json_file(data_dir, minimums_path)

        # Convert string keys to appropriate types
        minimums_converted = {}
        for cell_id_str, depth_bins in minimums_data.items():
            cell_id = int(cell_id_str)
            minimums_converted[cell_id] = {}

            for depth_bin_str, months in depth_bins.items():
                depth_bin = float(depth_bin_str)
                minimums_converted[cell_id][depth_bin] = {}

                for month_str, hourly_data in months.items():
                    month = int(month_str)
                    minimums_converted[cell_id][depth_bin][month] = hourly_data

        return Minimums(minimums_converted)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Minimums not found for scenario '{scenario_id}'"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Corrupt minimums data for scenario '{scenario_id}': {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading minimums for scenario '{scenario_id}': {str(e)}"
        )


def get_occupancy(scenario_id: str, cell_id: int, depth_bin: float) -> Occupancy:
    """Get occupancy timelines for a specific cell and depth bin.

    Args:
        scenario_id: Unique identifier for the scenario
        cell_id: Cell identifier
        depth_bin: Depth bin value

    Returns:
        Occupancy model with unwrapped timelines array (array of arrays, one timeline per model)

    Raises:
        HTTPException: If data not found, invalid parameters, or corrupt data
    """
    try:
        data_dir = get_data_dir()

        # First, get metadata to find depth_bin index and number of models
        meta_path = f"depth/{scenario_id}/meta_data.json"
        meta_data = read_json_file(data_dir, meta_path)

        depth_bins = meta_data.get("depth_bins", [])
        support = meta_data.get("support", [])

        if depth_bin not in depth_bins:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid depth_bin: {depth_bin}. Valid bins: {depth_bins}"
            )

        depth_bin_idx = depth_bins.index(depth_bin)
        num_depth_bins = len(depth_bins)
        num_models = len(support)

        # Read the parquet file for this cell
        occupancy_path = f"depth/{scenario_id}/{cell_id}_occupancy.parquet.gz"
        df = read_parquet_file(data_dir, occupancy_path)

        # Extract timelines for each model at the specified depth bin
        # Column index formula: model_idx * num_depth_bins + depth_bin_idx
        timelines = []
        for model_idx in range(num_models):
            col_idx = model_idx * num_depth_bins + depth_bin_idx
            if col_idx >= len(df.columns):
                raise HTTPException(
                    status_code=500,
                    detail=f"Column index {col_idx} out of range in occupancy data"
                )

            # Extract the column and convert to list, handling null values
            timeline = df.iloc[:, col_idx].tolist()
            timelines.append(timeline)

        return Occupancy(timelines)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Occupancy data not found for scenario '{scenario_id}', cell {cell_id}"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameters: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading occupancy data: {str(e)}"
        )
