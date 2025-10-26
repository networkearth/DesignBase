## `fishflow`

### Interfaces

Right now there is just one report `fishflow` builds:

`from fishflow.depth.report import build_report`

See `Depth/` for more details on this module. 

### Use Cases

This is a python package for generating reports that can be viewed in the `FishFlow` app using the `FishFlow` API. 

### Build

Need a `setup.py` at placement below. This should include any required dependencies for the `fishflow` package. 

`fishflow` is separated into report types that each have their own directory with all of their code. 

- `/depth` for designs in `Depth/`

There is also a `/common` directory for code used across different reports. 

#### Placement

```
fishflow
|
+-- reports
|   |
|   +-- setup.py <--
```

### Constraints

Should be installable by moving into:

`fishflow/reports/fishflow`

and running `pip install .`

#### Dependencies

```bash
- Python >= 3.9
- numpy >= 1.20.0
- pandas >= 1.3.0
- h3 >= 4.0.0 (or h3-py)
- pyarrow >= 6.0.0 (for parquet support)
- geojson >= 2.5.0
```

