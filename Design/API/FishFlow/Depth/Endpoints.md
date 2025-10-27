## Context

All data for this set of endpoints is stored at the `/depth` directory within the data directory specified by `FISHFLOW_DATA_DIR` (see `../Project.md`).
#### Data Schemas
The schemas and organization of this data can be found at `../../../Reports/FishFlow/Depth/Schemas.md` as these endpoints serve data from depth occupancy reports. 
#### Data Loading
All of these endpoints need to be capable of reading either from local disk or from `s3` depending on whether `FISHFLOW_DATA_DIR` points to an `s3` bucket or not. (`s3://` prefix)
#### Error Handling
These apply to all endpoints described herein.
- Bad request - 400
- No data - 404
- Corrupt data - 500

## `/v1/depth/scenario/scenarios`
### GET
#### Model
`fishflow_api/app/depth/models.py`

```python
Scenarios(scenarios=scenarios)
```

- `scenarios` - `List` of `Scenario` models

Models a list of scenarios (captured as their metadata).
#### Handler
`fishflow_api/app/depth/handlers.py`

```python
get_scenarios() --> Scenarios
```

Loops through the `/depth` directory and pulls each scenario to return a `Scenarios` model. Besides reorganizing the data there is no data transformation here.

Scenarios are identified by filtering for folders in the `/depth` directory.

## `/v1/depth/scenario/{scenario_id}/scenario`
### GET
#### Model
`fishflow_api/app/depth/models.py`

```python
Scenario(**scenario)
```
- `scenario` - a `dict` with all of the components found in `MetaDataSchema`

Model of `MetaDataSchema`
#### Handler
`fishflow_api/app/depth/handlers.py`

```python
get_scenario(scenario_id: str) --> Scenario
```

Simple pass through of metadata for the `scenario_id` specified.
## `/v1/depth/scenario/{scenario_id}/geometries`
### GET
#### Model
`fishflow_api/app/depth/models.py`

```python
Geometries(geojson)
```

- `geojson` - geojson as defined in `GeometriesSchema`

Model of `GeometriesSchema`
#### Handler
`fishflow_api/app/depth/handlers.py`

```python
get_geometries(scenario_id: str) --> Geometries
```

Simple pass through of geojson for the `scenario_id` specified.
#### Notes

Nothing should be added to the geojson. The top level keys should just be `type` and `features`.
## `/v1/depth/scenario/{scenario_id}/cell_depths`
### GET
#### Model
`fishflow_api/app/depth/models.py`

```python
CellDepths(cell_depths)
```

- `cell_depths` - a `dict` with all of the components found in `CellDepthsSchema`

Model of `CellDepthsSchema
#### Handler
`fishflow_api/app/depth/handlers.py`

```python
get_cell_depths(scenario_id: str) --> CellDepths
```

Simple pass through of cell_depths for the `scenario_id` specified. DO NOT wrap the dict. The format should be:

`{cell_id(int) -> maximum_depth_bin(float)}`

## `/v1/depth/scenario/{scenario_id}/timestamps`
### GET
#### Model
`fishflow_api/app/depth/models.py`

```python
Timestamps(timestamps)
```

- `timestamps` - a `list` as defined in `TimestampsSchema`

Model of `TimestampsSchema
#### Handler
`fishflow_api/app/depth/handlers.py`

```python
get_timestamps(scenario_id: str) --> Timestamps
```

Simple pass through of timestamps for the `scenario_id` specified.

DO NOT wrap the array. It should simply be an array of timestamps. 
## `/v1/depth/scenario/{scenario_id}/minimums`
### GET
#### Model
`fishflow_api/app/depth/models.py`

```python
Minimums(minimums)
```

- `minimums` - a `dict` with all of the components found in `MinimumsSchema`

Model of `MinimumsSchema`
#### Handler
`fishflow_api/app/depth/handlers.py`

```python
get_minimums(scenario_id: str) --> Minimums
```

Simple pass through of minimums for the `scenario_id` specified. DO NOT wrap the minimums. It should simply be:

`{cell_id(int) -> {depth_bin -> {month(int) -> minimums_array}}}`

`minimums_array` is the minimum depth occupancy in that cell and month per hour `0-23`. It is an array of length 24 containing floats.
## `/v1/depth/scenario/{scenario_id}/occupancy?cell_id={cell_id}&depth_bin={depth_bin}`
### GET
#### Model
`fishflow_api/app/depth/models.py`

```python
Occupancy(timelines)
```

- `timelines` - an array of likelihood timelines per model for a specific cell at a specific depth bin.

Model of the timelines for one cell and depth bin from `OccupancySchema`
#### Handler
`fishflow_api/app/depth/handlers.py`

```python
get_occupancy(scenario_id: str, cell_id: int, depth_bin: float) --> Occupancy
```

Example: `/v1/depth/scenario/{scenario_id}/occupancy?cell_id=123&depth_bin=10.5`

Pulls the timelines (as an array) for the `cell_id` and `depth_bin` in question. Note that because we have multiple models per report this will actually be an array of arrays:

`[model0_timeline, model1_timeline,..., modeln_timeline]`

See `OccupancySchema` for details on the data structure that we are pulling from for this endpoint.

To translate the `depth_bin` float parameter to a `depth_bin_idx`, find the index of the depth_bin in the `depth_bins` array from the metadata (see `MetaDataSchema`).