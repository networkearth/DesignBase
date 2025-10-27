# FishFlow Reports

A Python package for generating fish depth distribution reports using Bayesian model interpolation. This package creates reports viewable in the FishFlow app via the FishFlow API.

## Overview

FishFlow Reports implements Bayesian model interpolation to evaluate how much confidence we should have in complex fish behavior models compared to simpler reference models. The package generates comprehensive reports with spatial (H3-based) and temporal data showing fish depth distributions across a spectrum of model mixtures.

## Installation

From the directory where `setup.py` lives:

```bash
pip install .
```

For development with testing dependencies:

```bash
pip install -e ".[dev]"
```

## Requirements

- Python >= 3.9
- numpy >= 1.20.0
- pandas >= 1.3.0
- h3 >= 4.0.0
- pyarrow >= 6.0.0
- geojson >= 2.5.0

## Quick Start

Here's a minimal working example:

```python
import numpy as np
import pandas as pd
from datetime import datetime
from fishflow.depth.report import build_report

# Define metadata
meta_data = {
    "scenario_id": "example_scenario",
    "name": "Example Fish Depth Analysis",
    "species": "Atlantic Cod",
    "model": "Environmental Response Model",
    "reference_model": "Uniform Depth Distribution",
    "region": "Georges Bank",
    "reference_region": "North Atlantic",
    "description": "Analysis of cod depth preferences in response to temperature",
    "reference_time_window": ["2023-01-01 00:00:00", "2023-12-31 23:59:59"],
}

# Create sample model predictions
# For each decision (time-location), we have choices (depth bins) with probabilities
model_df = pd.DataFrame({
    "_decision": [1, 1, 2, 2, 3, 3],
    "_choice": ["10m", "20m", "10m", "20m", "10m", "20m"],
    "probability": [0.8, 0.2, 0.7, 0.3, 0.6, 0.4],
})

# Reference model assumes uniform distribution
reference_model_df = pd.DataFrame({
    "_decision": [1, 1, 2, 2, 3, 3],
    "_choice": ["10m", "20m", "10m", "20m", "10m", "20m"],
    "probability": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
})

# Context: spatial and temporal information for each decision-choice pair
context_df = pd.DataFrame({
    "_decision": [1, 1, 2, 2, 3, 3],
    "_choice": ["10m", "20m", "10m", "20m", "10m", "20m"],
    "datetime": [
        datetime(2024, 1, 1, 6, 0, 0),
        datetime(2024, 1, 1, 6, 0, 0),
        datetime(2024, 1, 1, 12, 0, 0),
        datetime(2024, 1, 1, 12, 0, 0),
        datetime(2024, 1, 1, 18, 0, 0),
        datetime(2024, 1, 1, 18, 0, 0),
    ],
    "h3_index": ["85283473fffffff"] * 6,  # H3 cell at resolution 5
    "depth_bin": [10.0, 20.0, 10.0, 20.0, 10.0, 20.0],
})

# Actual observations for computing model support
model_actuals_df = model_df.copy()
reference_model_actuals_df = reference_model_df.copy()

# Observed choices (one per decision)
selections_actuals_df = pd.DataFrame({
    "_decision": [1, 2, 3],
    "_choice": ["10m", "10m", "20m"],
})

# Define mixture family (0 = reference only, 1 = hypothesis only)
epsilons = np.linspace(0, 1, 11)

# Build report
build_report(
    meta_data=meta_data,
    model_df=model_df,
    reference_model_df=reference_model_df,
    context_df=context_df,
    model_actuals_df=model_actuals_df,
    reference_model_actuals_df=reference_model_actuals_df,
    selections_actuals_df=selections_actuals_df,
    epsilons=epsilons,
    data_dir="./output",
)
```

This creates the following directory structure:

```
output/
└── example_scenario/
    ├── meta_data.json
    ├── geometries.geojson
    ├── cell_depths.json
    ├── minimums.json
    ├── timestamps.json
    └── 0_occupancy.parquet.gz
```

## Core Concepts

### Bayesian Model Interpolation

Instead of choosing between a complex model and a simple reference model, this package computes a **family of mixture models** parameterized by epsilon (ε):

- **ε = 0**: Use only the reference model (e.g., uniform depth distribution)
- **ε = 1**: Use only the hypothesis model (e.g., environmental response model)
- **0 < ε < 1**: Blend both models

The package computes the posterior probability (support) for each mixture model given observed data, showing exactly how much the data supports model complexity.

### Key Functions

#### Computing Support

```python
from fishflow.common.support import compute_support

# Compute posterior probabilities across mixture family
support = compute_support(
    model_df=model_df,
    reference_model_df=reference_model_df,
    selections_df=selections_df,
    epsilons=np.linspace(0, 1, 21),
)
```

#### Computing Mixtures

```python
from fishflow.common.support import compute_mixtures

# Generate predictions for all mixture models
mixtures_df = compute_mixtures(
    model_df=model_df,
    reference_model_df=reference_model_df,
    epsilons=np.array([0.0, 0.5, 1.0]),
)
```

#### Spatial Processing

```python
from fishflow.common.spacetime import build_geojson_h3

# Convert H3 indices to GeoJSON polygons
geojson, cell_id_df = build_geojson_h3(context_df)
```

## Output Schema

### meta_data.json

Contains scenario metadata and derived statistics:

```json
{
  "scenario_id": "example_scenario",
  "name": "Example Fish Depth Analysis",
  "species": "Atlantic Cod",
  "model": "Environmental Response Model",
  "reference_model": "Uniform Depth Distribution",
  "region": "Georges Bank",
  "reference_region": "North Atlantic",
  "description": "Analysis of cod depth preferences",
  "time_window": ["2024-01-01 06:00:00", "2024-01-01 18:00:00"],
  "reference_time_window": ["2023-01-01 00:00:00", "2023-12-31 23:59:59"],
  "resolution": 5,
  "grid_size": 1,
  "depth_bins": [10.0, 20.0],
  "support": [0.05, 0.10, 0.15, 0.20, 0.25, 0.15, 0.05, 0.03, 0.01, 0.01, 0.00]
}
```

### geometries.geojson

GeoJSON FeatureCollection with H3 cell polygons:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lon1, lat1], [lon2, lat2], ...]]
      },
      "properties": {
        "cell_id": 0
      }
    }
  ]
}
```

### timestamps.json

Ordered array of timestamps:

```json
["2024-01-01 06:00:00", "2024-01-01 12:00:00", "2024-01-01 18:00:00"]
```

### cell_depths.json

Maximum depth per cell:

```json
{
  "0": 20.0,
  "1": 30.0
}
```

### minimums.json

Minimum occupancy probabilities by cell, depth, month, and hour:

```json
{
  "0": {
    "10.0": {
      "1": [0.3, 0.4, 0.5, ..., 0.3]
    }
  }
}
```

### {cell_id}_occupancy.parquet.gz

Compressed Parquet file with occupancy probabilities. Rows are timestamps, columns represent depth bins × mixture models. Column indexing: `model_idx = col // num_depth_bins`, `depth_bin_idx = col % num_depth_bins`.

## Testing

Run the test suite:

```bash
pip install pytest
pytest tests/
```

Run tests with coverage:

```bash
pip install pytest pytest-cov
pytest --cov=fishflow tests/
```

## Project Structure

```
fishflow/
├── setup.py
├── README.md
├── fishflow/
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── support.py       # Bayesian model interpolation functions
│   │   └── spacetime.py     # Spatial and temporal utilities
│   └── depth/
│       ├── __init__.py
│       └── report.py        # Report generation functions
└── tests/
    ├── test_support.py
    ├── test_spacetime.py
    └── test_report.py
```

## Implementation Notes

### Design Decisions

1. **Matrix-based computation**: The core likelihood calculations use NumPy matrices for efficiency with large datasets.

2. **Numerical stability**: Log-likelihood computations use the log-sum-exp trick to avoid numerical underflow.

3. **Cell-by-cell processing**: Reports process each spatial cell independently to manage memory with large grids.

4. **H3 spatial indexing**: Uses Uber's H3 hexagonal hierarchical spatial index for consistent spatial representation.

5. **Parquet compression**: Occupancy data is stored in compressed Parquet format for efficient storage and retrieval.

### Assumptions

- All model dataframes have consistent decision-choice pairs
- H3 indices are valid and at a consistent resolution
- Datetime values are comparable (same timezone or UTC)
- Depth bins are consistently defined across all data
- Selection data contains valid decision-choice pairs from the model data

### Error Handling

The package validates inputs and provides clear error messages for:
- Missing required columns in dataframes
- Mismatched decision-choice pairs between models
- Invalid epsilon values (must be in [0, 1])
- Invalid metadata (missing required fields)
- Shape mismatches in matrix operations

## License

[Add license information]

## Contributing

[Add contribution guidelines]

## Citation

If you use this package in your research, please cite:

[Add citation information]

## Support

For issues and questions:
- GitHub Issues: [Add repository URL]
- Documentation: [Add docs URL]
- Email: [Add contact email]
