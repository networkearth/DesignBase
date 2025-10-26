"""
FishFlow depth API module.

Provides endpoints for querying depth-related scenario data.
"""

from .endpoints import ENDPOINT_SPEC
from .models import (
    Scenarios,
    Scenario,
    Geometries,
    CellDepths,
    Timestamps,
    Minimums,
    Occupancy,
)
from .handlers import (
    get_scenarios,
    get_scenario,
    get_geometries,
    get_cell_depths,
    get_timestamps,
    get_minimums,
    get_occupancy,
)

__all__ = [
    "ENDPOINT_SPEC",
    "Scenarios",
    "Scenario",
    "Geometries",
    "CellDepths",
    "Timestamps",
    "Minimums",
    "Occupancy",
    "get_scenarios",
    "get_scenario",
    "get_geometries",
    "get_cell_depths",
    "get_timestamps",
    "get_minimums",
    "get_occupancy",
]
