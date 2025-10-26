"""
Endpoint specification for depth API.

Defines the mapping between URL paths, handler functions, and response models.
"""

from .handlers import (
    get_scenarios,
    get_scenario,
    get_geometries,
    get_cell_depths,
    get_timestamps,
    get_minimums,
    get_occupancy,
)
from .models import (
    Scenarios,
    Scenario,
    Geometries,
    CellDepths,
    Timestamps,
    Minimums,
    Occupancy,
)


# Endpoint specification mapping paths to (handler, response_model) tuples
ENDPOINT_SPEC = {
    "/v1/depth/scenario/scenarios": (get_scenarios, Scenarios),
    "/v1/depth/scenario/{scenario_id}/scenario": (get_scenario, Scenario),
    "/v1/depth/scenario/{scenario_id}/geometries": (get_geometries, Geometries),
    "/v1/depth/scenario/{scenario_id}/cell_depths": (get_cell_depths, CellDepths),
    "/v1/depth/scenario/{scenario_id}/timestamps": (get_timestamps, Timestamps),
    "/v1/depth/scenario/{scenario_id}/minimums": (get_minimums, Minimums),
    "/v1/depth/scenario/{scenario_id}/occupancy": (get_occupancy, Occupancy),
}
