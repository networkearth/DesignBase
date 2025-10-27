# FishFlow Reports

A Python package for generating depth occupancy reports using Bayesian model interpolation. These reports can be visualized in the FishFlow app via the FishFlow API.

## Overview

FishFlow Reports implements Bayesian model interpolation to quantify uncertainty in fish depth occupancy models. The package:

- Computes support (posterior probability) for model mixtures between a complex model and a simpler reference model
- Generates spatial-temporal occupancy reports using H3 hexagonal grids
- Produces compressed data outputs optimized for visualization in web applications

## Installation

From the directory containing `setup.py`:

```bash
pip install .
```

For development with tests:

```bash
pip install -e ".[dev]"
```

## Requirements

- Python >= 3.9
- numpy >= 1.20.0
- pandas >= 1.3.0
- h3 >= 4.0.0
- pyarrow >= 6.0.0 (for Parquet support)
- geojson >= 2.5.0

## Quick Start

```python
from fishflow.depth.report import build_report
import numpy as np
import pandas as pd

# Define metadata
meta_data = {
    'scenario_id': 'bluefin_2023',
    'name': 'Bluefin Tuna Depth Analysis 2023',
    'species': 'Bluefin Tuna',
    'model': 'Environmental Response Model',
    'reference_model': 'Uniform Depth Distribution',
    'region': 'Gulf of Mexico',
    'reference_region': 'Historical Data 2020-2022',
    'description': 'Depth occupancy analysis for bluefin tuna using environmental predictors',
    'reference_time_window': ['2020-01-01 00:00:00', '2022-12-31 23:59:59'],
    'zoom': 6,
    'center': [-88.0, 27.0]  # [longitude, latitude]
}

# Create model predictions dataframe
# Each row represents a choice (depth bin at a location-time) for a decision
model_df = pd.DataFrame({
    '_decision': [1, 1, 1, 2, 2, 2],  # Decision IDs
    '_choice': ['A', 'B', 'C', 'A', 'B', 'C'],  # Choice IDs
    'probability': [0.5, 0.3, 0.2, 0.6, 0.3, 0.1]  # Model predictions
})

# Create reference model predictions (same structure)
reference_model_df = pd.DataFrame({
    '_decision': [1, 1, 1, 2, 2, 2],
    '_choice': ['A', 'B', 'C', 'A', 'B', 'C'],
    'probability': [0.33, 0.33, 0.34, 0.33, 0.33, 0.34]  # Uniform
})

# Create context dataframe linking choices to space-time-depth
context_df = pd.DataFrame({
    '_decision': [1, 1, 1, 2, 2, 2],
    '_choice': ['A', 'B', 'C', 'A', 'B', 'C'],
    'datetime': ['2023-06-01 08:00:00'] * 3 + ['2023-06-01 12:00:00'] * 3,
    'h3_index': ['85283473fffffff'] * 3 + ['8528347bfffffff'] * 3,
    'depth_bin': [10.0, 20.0, 30.0, 10.0, 20.0, 30.0]
})

# Create validation/actuals data for computing support
model_actuals_df = pd.DataFrame({
    '_decision': [101, 101, 102, 102],
    '_choice': ['X', 'Y', 'X', 'Y'],
    'probability': [0.7, 0.3, 0.6, 0.4]
})

reference_model_actuals_df = pd.DataFrame({
    '_decision': [101, 101, 102, 102],
    '_choice': ['X', 'Y', 'X', 'Y'],
    'probability': [0.5, 0.5, 0.5, 0.5]
})

# Observed choices in validation data
selections_actuals_df = pd.DataFrame({
    '_decision': [101, 102],
    '_choice': ['X', 'X']
})

# Define mixture family density (0 = reference only, 1 = complex model only)
epsilons = np.linspace(0, 1, 21)

# Build the report
build_report(
    meta_data=meta_data,
    model_df=model_df,
    reference_model_df=reference_model_df,
    context_df=context_df,
    model_actuals_df=model_actuals_df,
    reference_model_actuals_df=reference_model_actuals_df,
    selections_actuals_df=selections_actuals_df,
    epsilons=epsilons,
    data_dir='./output'
)
```

## Output Structure

The `build_report` function creates a directory with the following structure:

```
{data_dir}/
└── {scenario_id}/
    ├── meta_data.json          # Scenario metadata and derived info
    ├── geometries.geojson      # H3 hexagon geometries with cell_ids
    ├── cell_depths.json        # Maximum depth per cell
    ├── minimums.json           # Minimum occupancy by cell/depth/month/hour
    ├── timestamps.json         # Ordered array of all timestamps
    ├── 0_occupancy.parquet.gz  # Occupancy time series for cell 0
    ├── 1_occupancy.parquet.gz  # Occupancy time series for cell 1
    └── ...
```

### File Descriptions

- **meta_data.json**: Contains scenario information including computed support values, depth bins, time windows, and map settings
- **geometries.geojson**: GeoJSON FeatureCollection of H3 hexagon polygons with cell_id properties
- **cell_depths.json**: Maps each cell_id to its maximum depth bin
- **minimums.json**: Nested structure with minimum occupancy probabilities per cell/depth/month/hour
- **timestamps.json**: Ordered list of ISO-formatted timestamps
- **{cell_id}_occupancy.parquet.gz**: Compressed Parquet files with occupancy probabilities where:
  - Rows are timestamps (in order from timestamps.json)
  - Columns represent model-depth combinations: `col = model_idx * n_depth_bins + depth_bin_idx`
  - Values are occupancy probabilities (NaN where depth exceeds cell maximum)

## Core Concepts

### Bayesian Model Interpolation

The package implements Bayesian model interpolation to measure confidence in model predictions. Instead of assuming a single "true" model, it evaluates a family of models parameterized by epsilon (ε):

- **ε = 0**: Pure reference model (e.g., uniform distribution)
- **ε = 1**: Pure complex model (e.g., environmental response model)
- **0 < ε < 1**: Mixture of both models

The posterior distribution over ε values represents how much the observed data supports each level of model complexity.

### Decision-Choice Framework

The package uses a decision-choice structure:

- **Decision**: A specific context (location + time) where the animal must "choose" a depth
- **Choice**: A possible depth bin at that location-time
- **Selection**: The actually observed choice in validation data

This framework allows flexible modeling of spatial-temporal depth preferences.

### H3 Spatial Indexing

The package uses Uber's H3 hexagonal hierarchical spatial index for spatial aggregation. H3 provides:

- Consistent hexagon sizes at each resolution
- Efficient spatial queries
- Clean visualization on maps

## Module Documentation

### fishflow.common.support

Core functions for Bayesian model interpolation:

- `log_likelihood_member()`: Compute log likelihood for a single mixture model
- `prob_members()`: Compute posterior probabilities across mixture family
- `build_model_matrices()`: Convert dataframes to matrix format
- `compute_support()`: High-level support computation
- `compute_mixtures()`: Generate mixture predictions for all epsilon values

### fishflow.common.spacetime

Spatial and temporal utilities:

- `build_geojson_h3()`: Create GeoJSON from H3 indices
- `build_timeline()`: Extract ordered timeline from data

### fishflow.depth.report

Report generation functions:

- `build_report()`: Main entry point for report generation
- `build_minimums()`: Compute minimum occupancy statistics
- `build_occupancy()`: Create occupancy time series dataframe
- `build_cell_depths()`: Extract maximum depth per cell

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=fishflow --cov-report=html
```

## Development Notes

### Assumptions Made During Implementation

1. **H3 Resolution**: Assumes all H3 indices in context data have the same resolution
2. **Datetime Format**: Accepts any pandas-parseable datetime format, outputs ISO 8601
3. **Choice Identifiers**: Choice and decision IDs can be any hashable type (strings, ints, etc.)
4. **Probability Normalization**: Assumes input probabilities are already properly normalized per decision
5. **Missing Data**: NaN values in occupancy arrays indicate depth bins that exceed the cell's maximum depth

### Performance Considerations

- The package processes cells sequentially to manage memory usage with large datasets
- Occupancy files are compressed with gzip to reduce storage requirements
- Matrix operations use NumPy for efficient computation

### Error Handling

All functions include input validation with descriptive error messages for:
- Missing required columns
- Incompatible dataframe structures
- Invalid parameter ranges
- Mismatched data between model and reference predictions

## License

[Your license here]

## Citation

If you use this package in research, please cite:

[Your citation here]

## Contact

[Your contact information here]
