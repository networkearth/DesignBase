# FishFlow Reports

A Python package for generating depth occupancy reports for the FishFlow application.

## Overview

FishFlow Reports implements Bayesian Model Interpolation to measure confidence in depth prediction models by computing model mixtures that interpolate between a reference model and a target model. The package generates reports containing spatial-temporal occupancy data that can be consumed by the FishFlow API and visualized in the FishFlow app.

## Features

- **Bayesian Model Interpolation**: Compute support across a family of models that blend a reference model with a target model
- **Spatial Data Handling**: Work with H3 hexagonal spatial indices and generate GeoJSON representations
- **Temporal Analysis**: Process time-series data and generate timeline metadata
- **Efficient Processing**: Build reports one cell at a time to handle large datasets
- **Production-Ready**: Comprehensive error handling, input validation, and type hints

## Installation

### Prerequisites

- Python >= 3.9
- pip

### From Source

1. Navigate to the package directory:
```bash
cd fishflow/reports
```

2. Install the package:
```bash
pip install .
```

Or for development with testing dependencies:
```bash
pip install -e ".[dev]"
```

## Dependencies

The package requires the following dependencies (automatically installed):

- `numpy >= 1.20.0` - Numerical computing
- `pandas >= 1.3.0` - Data manipulation
- `h3 >= 4.0.0` - H3 hexagonal spatial indexing
- `pyarrow >= 6.0.0` - Parquet file support
- `geojson >= 2.5.0` - GeoJSON handling

## Usage

### Basic Example

```python
import numpy as np
import pandas as pd
from fishflow.depth.report import build_report

# Prepare your data
meta_data = {
    'scenario_id': 'my_scenario_001',
    'name': 'Example Depth Analysis',
    'species': 'Tuna',
    'model': 'target_model_v1',
    'reference_model': 'baseline_model_v1',
    'region': 'pacific_northwest',
    'reference_region': 'pacific_northwest',
    'description': 'Fish depth analysis',
    'time_window': ['2023-01-01T00:00:00', '2023-01-31T23:59:59'],
    'reference_time_window': ['2022-01-01T00:00:00', '2022-01-31T23:59:59'],
    'grid_size': 100,
    'depth_bins': [0.0, 10.0, 20.0, 30.0, 40.0],
    'resolution': 7,
    'support': [0.05, 0.10, 0.15, 0.20, 0.15, 0.10, 0.08, 0.07, 0.05, 0.03, 0.02]
}

# Model predictions (target model)
model_df = pd.DataFrame({
    '_decision': [1, 1, 2, 2],
    '_choice': ['location_A', 'location_B', 'location_A', 'location_B'],
    'probability': [0.8, 0.2, 0.7, 0.3]
})

# Reference model predictions (simpler baseline)
reference_model_df = pd.DataFrame({
    '_decision': [1, 1, 2, 2],
    '_choice': ['location_A', 'location_B', 'location_A', 'location_B'],
    'probability': [0.5, 0.5, 0.5, 0.5]
})

# Context information
context_df = pd.DataFrame({
    '_decision': [1, 1, 2, 2],
    '_choice': ['location_A', 'location_B', 'location_A', 'location_B'],
    'datetime': pd.to_datetime([
        '2023-01-01 10:00', '2023-01-01 10:00',
        '2023-01-01 11:00', '2023-01-01 11:00'
    ]),
    'h3_index': [
        '85283473fffffff', '8528342bfffffff',
        '85283473fffffff', '8528342bfffffff'
    ],
    'depth_bin': [0, 1, 0, 1]
})

# Actual observations for support calculation
model_actuals_df = pd.DataFrame({
    '_decision': [1, 1],
    '_choice': ['location_A', 'location_B'],
    'probability': [0.8, 0.2]
})

reference_actuals_df = pd.DataFrame({
    '_decision': [1, 1],
    '_choice': ['location_A', 'location_B'],
    'probability': [0.5, 0.5]
})

selections_actuals_df = pd.DataFrame({
    '_decision': [1],
    '_choice': ['location_A']
})

# Define model family (epsilon values from 0 to 1)
epsilons = np.linspace(0, 1, 11)  # 11 models from pure reference to pure target

# Build the report
build_report(
    meta_data=meta_data,
    model_df=model_df,
    reference_model_df=reference_model_df,
    context_df=context_df,
    model_actuals_df=model_actuals_df,
    reference_model_actuals_df=reference_actuals_df,
    selections_actuals_df=selections_actuals_df,
    epsilons=epsilons,
    data_dir='/path/to/output'
)
```

### Output Structure

The `build_report` function creates the following directory structure:

```
/path/to/output/
└── my_scenario_001/
    ├── meta_data.json         # Scenario metadata
    ├── geometries.geojson     # H3 cell geometries
    ├── cell_depths.json       # Maximum depth per cell
    ├── timestamps.json        # Sorted unique timestamps
    ├── minimums.json          # Minimum probabilities by cell/depth/time
    ├── support.json           # Model support (posterior probabilities)
    ├── 0_occupancy.parquet.gz # Occupancy data for cell 0
    ├── 1_occupancy.parquet.gz # Occupancy data for cell 1
    └── ...                    # One parquet file per cell
```

## API Reference

### Main Functions

#### `build_report`

Build a complete depth occupancy report.

**Parameters:**
- `meta_data` (dict): Metadata including 'scenario_id'
- `model_df` (DataFrame): Target model predictions with columns `_decision`, `_choice`, `probability`
- `reference_model_df` (DataFrame): Reference model predictions
- `context_df` (DataFrame): Context with `_decision`, `_choice`, `datetime`, `h3_index`, `depth_bin`
- `model_actuals_df` (DataFrame): Target model predictions on actual data
- `reference_model_actuals_df` (DataFrame): Reference model predictions on actual data
- `selections_actuals_df` (DataFrame): Actually observed selections (`_decision`, `_choice`)
- `epsilons` (array): Mixing parameters (0 to 1) defining the model family
- `data_dir` (str): Output directory

### Support Functions

#### `compute_support`

Compute posterior probabilities (support) for each model in the mixture family.

```python
from fishflow.common.support import compute_support

support = compute_support(model_df, reference_model_df, selections_df, epsilons)
```

#### `compute_mixtures`

Compute interpolated probabilities for all models in the family.

```python
from fishflow.common.support import compute_mixtures

mixtures_df = compute_mixtures(model_df, reference_model_df, epsilons)
```

### Spatial Functions

#### `build_geojson_h3`

Convert H3 indices to GeoJSON representation.

```python
from fishflow.common.spacetime import build_geojson_h3

geojson, cell_id_df = build_geojson_h3(context_df)
```

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=fishflow --cov-report=html
```

## Data Format Requirements

### Input DataFrames

**model_df / reference_model_df:**
- `_decision`: Decision identifier
- `_choice`: Choice identifier
- `probability`: Model probability for this choice

**context_df:**
- `_decision`: Decision identifier (matches model_df)
- `_choice`: Choice identifier (matches model_df)
- `datetime`: Timestamp (pandas datetime or ISO string)
- `h3_index`: H3 hexagonal cell index (string)
- `depth_bin`: Depth bin identifier (integer)

**selections_actuals_df:**
- `_decision`: Decision identifier
- `_choice`: Actually selected choice (one per decision)

### Validation

The package validates:
- Model and reference model have identical `(_decision, _choice)` pairs
- All required columns are present
- Epsilon values are in [0, 1]
- Each decision has exactly one selection
- Valid H3 indices

## Assumptions and Decisions

This implementation makes the following decisions for unspecified details:

1. **Cell IDs**: Assigned as integers starting from 0 in alphabetical order of H3 indices
2. **Month Indexing**: Months are 0-indexed (0-11, where 0 is January)
3. **Hour Indexing**: Hours are 0-indexed (0-23)
4. **Datetime Format**: Timestamps are stored in ISO 8601 format
5. **Parquet Compression**: Uses gzip compression for occupancy files
6. **Directory Handling**: Existing scenario directories are overwritten
7. **Error Handling**: Raises `ValueError` with descriptive messages for invalid inputs
8. **Numerical Stability**: Uses log-sum-exp trick in Bayesian computations

## Performance Considerations

- Reports are built one cell at a time to manage memory with large datasets
- Progress is printed to stdout during report generation
- Occupancy files are compressed with gzip to reduce storage

## License

MIT License

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- New features include tests
- Code follows existing style conventions
- Docstrings use Google/NumPy style

## Support

For issues or questions, please refer to the design documents in the `Design/FishFlow/Reports/` directory.
