"""
Handler functions for FishFlow depth API endpoints.

These functions handle the business logic for each endpoint, including
data retrieval, validation, and transformation.
"""

from typing import List, Optional
from fastapi import HTTPException, Query

from .models import (
    Scenarios,
    Scenario,
    Geometries,
    CellDepths,
    Timestamps,
    Minimums,
    Occupancy,
)
from .data_access import (
    get_data_root,
    list_directories,
    read_json_file,
    read_geojson_file,
    read_parquet_file,
)


def get_scenarios() -> Scenarios:
    """
    Retrieve all available scenarios.

    Loops through the /depth directory and pulls metadata for each scenario.
    Scenarios are identified by filtering for folders in the /depth directory.

    Returns:
        Scenarios object containing list of all scenario metadata

    Raises:
        HTTPException: 500 if unable to access data directory or read files
    """
    try:
        data_root = get_data_root()
        scenario_ids = list_directories(data_root)

        scenarios = []
        for scenario_id in scenario_ids:
            try:
                meta_data = read_json_file(data_root, scenario_id, "meta_data.json")
                scenarios.append(Scenario(**meta_data))
            except HTTPException as e:
                # If a specific scenario can't be read, skip it but continue
                # This allows the API to work even if some scenarios are corrupted
                continue
            except Exception as e:
                # Skip malformed scenarios
                continue

        return Scenarios(scenarios=scenarios)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving scenarios: {str(e)}"
        )


def get_scenario(scenario_id: str) -> Scenario:
    """
    Retrieve metadata for a specific scenario.

    Simple pass through of metadata for the scenario_id specified.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Scenario object containing the scenario metadata

    Raises:
        HTTPException: 404 if scenario_id does not exist
        HTTPException: 500 if unable to access data directory or read files
    """
    try:
        data_root = get_data_root()
        meta_data = read_json_file(data_root, scenario_id, "meta_data.json")
        return Scenario(**meta_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving scenario: {str(e)}"
        )


def get_geometries(scenario_id: str) -> Geometries:
    """
    Retrieve GeoJSON geometries for a specific scenario.

    Simple pass through of geojson for the scenario_id specified.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Geometries object containing the GeoJSON data

    Raises:
        HTTPException: 404 if scenario_id does not exist
        HTTPException: 500 if unable to access data directory or read files
    """
    try:
        data_root = get_data_root()
        geojson = read_geojson_file(data_root, scenario_id)
        return Geometries(geojson=geojson)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving geometries: {str(e)}"
        )


def get_cell_depths(scenario_id: str) -> CellDepths:
    """
    Retrieve cell depth mappings for a specific scenario.

    Simple pass through of cell_depths for the scenario_id specified.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        CellDepths object containing the cell depth mappings

    Raises:
        HTTPException: 404 if scenario_id does not exist
        HTTPException: 500 if unable to access data directory or read files
    """
    try:
        data_root = get_data_root()
        cell_depths_data = read_json_file(data_root, scenario_id, "cell_depths.json")

        # Convert keys to strings for consistency
        cell_depths_str = {str(k): v for k, v in cell_depths_data.items()}

        return CellDepths(cell_depths=cell_depths_str)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving cell depths: {str(e)}"
        )


def get_timestamps(scenario_id: str) -> Timestamps:
    """
    Retrieve timestamps for a specific scenario.

    Simple pass through of timestamps for the scenario_id specified.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Timestamps object containing the ordered array of timestamps

    Raises:
        HTTPException: 404 if scenario_id does not exist
        HTTPException: 500 if unable to access data directory or read files
    """
    try:
        data_root = get_data_root()
        timestamps_data = read_json_file(data_root, scenario_id, "timestamps.json")

        # The JSON file should contain an array directly
        if isinstance(timestamps_data, list):
            return Timestamps(timestamps=timestamps_data)
        else:
            raise HTTPException(
                status_code=500,
                detail="Malformed timestamps.json: expected array"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving timestamps: {str(e)}"
        )


def get_minimums(scenario_id: str) -> Minimums:
    """
    Retrieve minimum occupancy data for a specific scenario.

    Simple pass through of minimums for the scenario_id specified.

    Args:
        scenario_id: Unique identifier for the scenario

    Returns:
        Minimums object containing the minimum occupancy data

    Raises:
        HTTPException: 404 if scenario_id does not exist
        HTTPException: 500 if unable to access data directory or read files
    """
    try:
        data_root = get_data_root()
        minimums_data = read_json_file(data_root, scenario_id, "minimums.json")

        # Convert all keys to strings for consistency
        minimums_str = {}
        for cell_id, depth_bins in minimums_data.items():
            minimums_str[str(cell_id)] = {}
            for depth_bin, months in depth_bins.items():
                minimums_str[str(cell_id)][str(depth_bin)] = {}
                for month, values in months.items():
                    minimums_str[str(cell_id)][str(depth_bin)][str(month)] = values

        return Minimums(minimums=minimums_str)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving minimums: {str(e)}"
        )


def get_occupancy(
    scenario_id: str,
    cell_id: int = Query(..., description="Cell ID to query"),
    depth_bin: float = Query(..., description="Depth bin to query"),
) -> Occupancy:
    """
    Retrieve occupancy timelines for a specific cell and depth bin.

    Pulls the timelines (as an array) for the cell_id and depth_bin in question.
    Returns an array of arrays: [model0_timeline, model1_timeline,..., modeln_timeline]

    Args:
        scenario_id: Unique identifier for the scenario
        cell_id: Cell ID to query (from query parameter)
        depth_bin: Depth bin value to query (from query parameter)

    Returns:
        Occupancy object containing timelines for all models at the specified cell and depth

    Raises:
        HTTPException: 400 if cell_id or depth_bin are missing or invalid
        HTTPException: 400 if depth_bin is not found in the scenario's depth_bins
        HTTPException: 404 if scenario_id does not exist
        HTTPException: 404 if parquet file for cell_id does not exist
        HTTPException: 500 if unable to access data directory or read files
    """
    try:
        # Validate inputs
        if cell_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required query parameter: cell_id"
            )
        if depth_bin is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required query parameter: depth_bin"
            )

        data_root = get_data_root()

        # Get scenario metadata to find depth_bins and number of models
        meta_data = read_json_file(data_root, scenario_id, "meta_data.json")
        scenario = Scenario(**meta_data)

        # Find the depth_bin index
        try:
            depth_bin_idx = scenario.depth_bins.index(depth_bin)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Depth bin {depth_bin} not found in scenario's depth bins"
            )

        # Read the parquet file for this cell
        df = read_parquet_file(data_root, scenario_id, cell_id)

        # Calculate which columns we need
        # model_idx = col // num_depth_bins
        # depth_bin_idx = col % num_depth_bins
        num_depth_bins = len(scenario.depth_bins)
        num_models = len(scenario.support)

        # Extract timelines for each model at this depth_bin
        timelines = []
        for model_idx in range(num_models):
            col_idx = model_idx * num_depth_bins + depth_bin_idx

            if col_idx < len(df.columns):
                # Extract the column and convert to list
                # Handle NaN/null values
                timeline = df.iloc[:, col_idx].tolist()
                timelines.append(timeline)
            else:
                # If column doesn't exist, return None timeline
                timelines.append([None] * len(df))

        return Occupancy(timelines=timelines)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving occupancy: {str(e)}"
        )
