## `fishflow`

### Interfaces

Right now there is just one report `fishflow` builds:

`from fishflow import depth_report`

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
|   +-- fishflow
|   |   |
|   |   +-- setup.py <--
```

### Constraints

Should be installable by moving into:

`fishflow/reports/fishflow`

and running `pip install .`

