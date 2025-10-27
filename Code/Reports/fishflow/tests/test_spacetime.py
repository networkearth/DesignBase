"""
Unit tests for fishflow.common.spacetime module.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from fishflow.common.spacetime import build_geojson_h3, build_timeline


class TestBuildGeojsonH3:
    """Tests for build_geojson_h3 function."""

    def test_basic_conversion(self):
        """Test basic H3 to GeoJSON conversion."""
        # Use a real H3 index at resolution 5
        h3_index = "85283473fffffff"

        context_df = pd.DataFrame(
            {
                "_decision": [1, 1, 2, 2],
                "_choice": ["A", "B", "A", "B"],
                "h3_index": [h3_index, h3_index, h3_index, h3_index],
            }
        )

        geojson, cell_id_df = build_geojson_h3(context_df)

        # Check GeoJSON structure
        assert geojson["type"] == "FeatureCollection"
        assert "features" in geojson
        assert len(geojson["features"]) == 1  # One unique H3 index

        feature = geojson["features"][0]
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Polygon"
        assert "cell_id" in feature["properties"]
        assert feature["properties"]["cell_id"] == 0

        # Check cell_id_df
        assert len(cell_id_df) == 4
        assert all(cell_id_df["cell_id"] == 0)
        assert "_decision" in cell_id_df.columns
        assert "_choice" in cell_id_df.columns

    def test_multiple_cells(self):
        """Test with multiple unique H3 indices."""
        h3_indices = ["85283473fffffff", "8528342bfffffff", "85283447fffffff"]

        context_df = pd.DataFrame(
            {
                "_decision": [1, 2, 3],
                "_choice": ["A", "A", "A"],
                "h3_index": h3_indices,
            }
        )

        geojson, cell_id_df = build_geojson_h3(context_df)

        # Should have 3 features
        assert len(geojson["features"]) == 3

        # Cell IDs should be 0, 1, 2 in alphabetical order of H3 indices
        sorted_h3 = sorted(h3_indices)
        for i, feature in enumerate(geojson["features"]):
            expected_cell_id = sorted_h3.index(
                context_df[context_df["_decision"] == i + 1]["h3_index"].iloc[0]
            )
            # Find the feature with this cell_id
            matching_features = [
                f for f in geojson["features"]
                if f["properties"]["cell_id"] == expected_cell_id
            ]
            assert len(matching_features) == 1

    def test_alphabetical_ordering(self):
        """Test that cell IDs follow alphabetical order of H3 indices."""
        # Create H3 indices that are not in alphabetical order in the dataframe
        h3_indices = ["85283473fffffff", "8528342bfffffff", "85283447fffffff"]
        # In alphabetical order: 8528342bfffffff (0), 85283447fffffff (1), 85283473fffffff (2)

        context_df = pd.DataFrame(
            {
                "_decision": [1, 2, 3],
                "_choice": ["A", "A", "A"],
                "h3_index": h3_indices,
            }
        )

        geojson, cell_id_df = build_geojson_h3(context_df)

        # Check mapping
        mapping = dict(zip(cell_id_df["_decision"], cell_id_df["cell_id"]))

        # The first decision (85283473fffffff) should get cell_id 2
        assert mapping[1] == sorted(h3_indices).index("85283473fffffff")

    def test_missing_columns(self):
        """Test that missing columns raise error."""
        context_df = pd.DataFrame(
            {
                "_decision": [1, 2],
                "h3_index": ["85283473fffffff", "8528342bfffffff"],
            }
        )

        with pytest.raises(ValueError, match="must contain columns"):
            build_geojson_h3(context_df)


class TestBuildTimeline:
    """Tests for build_timeline function."""

    def test_basic_timeline(self):
        """Test basic timeline extraction."""
        dates = [
            datetime(2024, 1, 1, 0, 0, 0),
            datetime(2024, 1, 2, 0, 0, 0),
            datetime(2024, 1, 3, 0, 0, 0),
        ]

        context_df = pd.DataFrame(
            {
                "_decision": [1, 2, 3],
                "_choice": ["A", "A", "A"],
                "datetime": dates,
            }
        )

        timeline = build_timeline(context_df)

        # Should be sorted array
        assert isinstance(timeline, np.ndarray)
        assert len(timeline) == 3
        assert all(timeline[i] <= timeline[i + 1] for i in range(len(timeline) - 1))

    def test_duplicate_removal(self):
        """Test that duplicate datetimes are removed."""
        date1 = datetime(2024, 1, 1, 0, 0, 0)
        date2 = datetime(2024, 1, 2, 0, 0, 0)

        context_df = pd.DataFrame(
            {
                "_decision": [1, 2, 3, 4],
                "_choice": ["A", "A", "A", "A"],
                "datetime": [date1, date1, date2, date2],
            }
        )

        timeline = build_timeline(context_df)

        # Should only have 2 unique dates
        assert len(timeline) == 2

    def test_sorting(self):
        """Test that timeline is sorted."""
        dates = [
            datetime(2024, 1, 3, 0, 0, 0),
            datetime(2024, 1, 1, 0, 0, 0),
            datetime(2024, 1, 2, 0, 0, 0),
        ]

        context_df = pd.DataFrame(
            {
                "_decision": [1, 2, 3],
                "_choice": ["A", "A", "A"],
                "datetime": dates,
            }
        )

        timeline = build_timeline(context_df)

        # Should be in sorted order
        assert timeline[0] == datetime(2024, 1, 1, 0, 0, 0)
        assert timeline[1] == datetime(2024, 1, 2, 0, 0, 0)
        assert timeline[2] == datetime(2024, 1, 3, 0, 0, 0)

    def test_missing_columns(self):
        """Test that missing columns raise error."""
        context_df = pd.DataFrame(
            {
                "_decision": [1, 2],
                "datetime": [
                    datetime(2024, 1, 1, 0, 0, 0),
                    datetime(2024, 1, 2, 0, 0, 0),
                ],
            }
        )

        with pytest.raises(ValueError, match="must contain columns"):
            build_timeline(context_df)
