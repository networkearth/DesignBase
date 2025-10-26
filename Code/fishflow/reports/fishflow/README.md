# FishFlow Reports

A Python package for generating depth occupancy reports for the FishFlow application.

## Overview

The `fishflow` package implements Bayesian model interpolation for depth prediction models, generating comprehensive reports that include spatial geometries, temporal timelines, occupancy probabilities, and confidence metrics.

## Features

- **Bayesian Model Interpolation**: Compute posterior support for model mixtures
- **Spatial Processing**: Convert H3 hexagon indices to GeoJSON geometries
- **Temporal Analysis**: Extract and organize timeline data
- **Occupancy Reports**: Generate depth occupancy matrices for visualization
- **Confidence Metrics**: Compute minimum probabilities across time dimensions

## Installation

### Prerequisites

- Python >= 3.9
- pip

### Install from source

1. Navigate to the package directory:
   ```bash
   cd fishflow/reports/fishflow
   ```

2. Install using pip:
   ```bash
   pip install .
   ```

   Or for development (editable install):
   ```bash
   pip install -e .
   ```

## Dependencies

The package automatically installs the following dependencies:

- numpy >= 1.20.0
- pandas >= 1.3.0
- h3 >= 3.7.0 (or h3-py)
- pyarrow >= 6.0.0 (for parquet support)
- geojson >= 2.5.0

## Usage

### Basic Usage

```python
from fishflow.depth.report import build_report
import numpy as np
import pandas as pd

# Prepare your data
meta_data = {
    'scenario_id': 'scenario_001',
    'description': 'Depth analysis for region A'
}

# Model predictions (example structure)
model_df = pd.DataFrame({
    '_decision': [1, 1, 2, 2],
    '_choice': ['A', 'B', 'A', 'B'],
    'probability': [0.4, 0.6, 0.3, 0.7]
})

reference_model_df = pd.DataFrame({
    '_decision': [1, 1, 2, 2],
    '_choice': ['A', 'B', 'A', 'B'],
    'probability': [0.5, 0.5, 0.5, 0.5]
})

# Context data
context_df = pd.DataFrame({
    '_decision': [1, 1, 2, 2],
    '_choice': ['A', 'B', 'A', 'B'],
    'datetime': ['2024-01-01 10:00', '2024-01-01 10:00',
                 '2024-01-01 11:00', '2024-01-01 11:00'],
    'h3_index': ['87283080fffffff', '87283082fffffff',
                 '87283080fffffff', '87283082fffffff'],
    'depth_bin': [1, 2, 1, 2]
})

# Actuals data
model_actuals_df = pd.DataFrame({
    '_decision': [1, 1, 2, 2],
    '_choice': ['A', 'B', 'A', 'B'],
    'probability': [0.35, 0.65, 0.25, 0.75]
})

reference_model_actuals_df = pd.DataFrame({
    '_decision': [1, 1, 2, 2],
    '_choice': ['A', 'B', 'A', 'B'],
    'probability': [0.5, 0.5, 0.5, 0.5]
})

selections_actuals_df = pd.DataFrame({
    '_decision': [1, 2],
    '_choice': ['A', 'B']
})

# Define mixture family
epsilons = np.linspace(0, 1, 11)  # 11 models from pure reference to pure model

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

### Output Structure

The `build_report` function creates the following directory structure:

```
output/
└── scenario_001/
    ├── meta_data.json           # Scenario metadata
    ├── geometries.geojson       # H3 hexagon geometries with cell IDs
    ├── cell_depths.json         # Maximum depth bin per cell
    ├── minimums.json            # Minimum probabilities by cell/depth/time
    ├── timestamps.json          # Ordered array of unique timestamps
    ├── support.json             # Posterior support for each epsilon
    ├── 0_occupancy.parquet.gz   # Occupancy matrix for cell 0
    ├── 1_occupancy.parquet.gz   # Occupancy matrix for cell 1
    └── ...                      # One occupancy file per cell
```

### Using Individual Functions

You can also use individual functions from the package:

```python
from fishflow.common.support import compute_support, compute_mixtures
from fishflow.common.spacetime import build_geojson_h3, build_timeline
from fishflow.depth.report import build_cell_depths, build_occupancy, build_minimums

# Compute support for model mixture
support = compute_support(
    model_actuals_df,
    reference_model_actuals_df,
    selections_actuals_df,
    epsilons
)

# Compute mixtures
mixtures_df = compute_mixtures(
    model_df,
    reference_model_df,
    epsilons
)

# Build spatial geometries
geojson_data, cell_id_df = build_geojson_h3(context_df)

# Extract timeline
timeline = build_timeline(context_df)

# Get cell depths
cell_depths = build_cell_depths(context_df)
```

## Data Format Requirements

### Model DataFrames
Must contain columns:
- `_decision`: Decision identifier (any hashable type)
- `_choice`: Choice identifier (any hashable type)
- `probability`: Probability value (float, 0-1)

### Context DataFrame
Must contain columns:
- `_decision`: Decision identifier
- `_choice`: Choice identifier
- `datetime`: Timestamp (datetime or parseable string)
- `h3_index`: H3 hexagon index (string)
- `depth_bin`: Depth bin identifier (int)

### Selections DataFrame
Must contain columns:
- `_decision`: Decision identifier
- `_choice`: Actually selected choice (one per decision)

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run specific test modules:

```bash
python -m pytest tests/test_support.py
python -m pytest tests/test_spacetime.py
python -m pytest tests/test_depth_report.py
```

## Understanding the Model Mixture Approach

This package implements Bayesian model interpolation to measure confidence in predictions. The key concept:

- **Reference Model (ε=0)**: A simple, conservative baseline model
- **Complex Model (ε=1)**: A detailed, feature-rich prediction model
- **Mixture Family (0≤ε≤1)**: A continuum of models interpolating between the two

The `support` array returned by the analysis tells you where along this continuum the data provides the most support. A support distribution peaked near ε=1 indicates strong evidence for the complex model, while a peak near ε=0 suggests the data favors simplicity.

## Implementation Notes

### Assumptions Made

Where the design documents were ambiguous, the following decisions were made:

1. **Error Handling**: Input validation raises `ValueError` with descriptive messages
2. **Data Types**: Numeric computations use NumPy for efficiency
3. **File Overwriting**: If a scenario directory exists, it's completely removed and recreated
4. **Datetime Serialization**: Datetimes are converted to ISO format strings for JSON
5. **Dictionary Key Types**: JSON files use string keys (integers converted to strings)
6. **Numerical Stability**: Log-space computations prevent underflow in likelihood calculations

### Performance Considerations

The `build_report` function processes cells one at a time to manage memory usage when dealing with large datasets. This sequential processing ensures the system can handle scenarios with many cells without running out of memory.

## Contributing

When contributing to this package:

1. Maintain type hints on all function signatures
2. Include Google-style docstrings for all public functions
3. Add unit tests for new functionality
4. Validate inputs early and provide clear error messages
5. Follow existing code style and conventions

## License

[Your license information here]

## Support

For issues, questions, or contributions, please contact the FishFlow development team.
