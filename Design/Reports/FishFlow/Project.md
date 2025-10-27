## Summary
This is a python package for generating reports that can be viewed in the `FishFlow` app using the `FishFlow` API. 

## Installation
From the directory where `setup.py` lives:
```bash
pip install .
```

## Structure
```bash
fishflow/
+-- setup.py
+-- fishflow/
|   +-- __init__.py
|   +-- common/
|   |   +-- support.py
|   |   +-- spacetime.py
|   +-- depth/
|   |   +-- report.py
+-- tests/
|   +-- test_report.py
|   +-- test_support.py
|   +-- test_spacetime.py
```

## Stack
```bash
Python >= 3.9
numpy >= 1.20.0
pandas >= 1.3.0
h3 >= 4.0.0 (or h3-py)
pyarrow >= 6.0.0 (for parquet support)
geojson >= 2.5.0
```

## Further Designs
- `Common/`
- `Depth/`

