## Summary
This is a python package for generating reports that can be viewed in the `FishFlow` app using the `FishFlow` API. 

## Installation
From the directory where `setup.py` lives:
```bash
pip install .
```

## Setup
```python
setuptools.setup(
    name="fishflow",
    version="0.1.0",
    packages=["fishflow", "fishflow.common", "fishflow.depth"],
    install_requires=[...],
    python_requires=">=3.9"
)
```
## Structure
```bash
fishflow/
+-- setup.py
+-- fishflow/
|   +-- __init__.py
|   +-- common/
|   |   +-- __init__.py
|   |   +-- support.py
|   |   +-- spacetime.py
|   +-- depth/
|   |   +-- __init__.py
|   |   +-- report.py
+-- tests/
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

## Tests
Should be selected and added by the LLM. 

## Further Designs
- `Common/`
- `Depth/`

