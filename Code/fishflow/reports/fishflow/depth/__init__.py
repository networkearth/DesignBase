"""
Depth report module for FishFlow.
"""

from .report import (
    build_report,
    build_cell_depths,
    build_occupancy,
    build_minimums
)

__all__ = [
    'build_report',
    'build_cell_depths',
    'build_occupancy',
    'build_minimums',
]
