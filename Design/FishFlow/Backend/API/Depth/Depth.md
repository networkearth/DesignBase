## `ENDPOINT_SPEC`

### Interfaces

N/A

### Use Cases

Captures the endpoints for the `v1/depth` endpoint class.

Used by `../API.md:register_endpoint_spec`

### Build

```python
{
	"/v1/depth/scenario/scenarios": (get_scenarios, Scenarios),
	"/v1/depth/scenario/{scenario_id}/scenario": (get_scenario, Scenario),
	"/v1/depth/scenario/{scenario_id}/geometries": (get_geometries, Geometries),
	"/v1/depth/scenario/{scenario_id}/cell_depths": (get_cell_depths, CellDepths),
	"/v1/depth/scenario/{scenario_id}/timestamps": (get_timestamps, Timestamps),
	"/v1/depth/scenario/{scenario_id}/minimums": (get_minimums, Minimums),
	"/v1/depth/scenario/{scenario_id}/occupancy": (get_occupancy, Occupancy),
}
```

#### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- endpoints.py <--
```

### Constraints

N/A

## `get_scenarios`

### Interfaces

```python
get_scenarios() --> Scenarios
```

### Use Cases

Loops through the `/depth` directory and pulls each scenario to return a `Scenarios` model. Besides reorganizing the data there is no data transformation here.

Scenarios are identified by filtering for folders in the `/depth` directory.

### Build

The data structure can be found in `Data.md`

Dependent on `Scenarios`

### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- handlers.py <--
```
### Constraints

Needs to be capable of reading either from local disk or from `s3` depending on whether `FishFlowData` points to an `s3` bucket or not. (`s3://` prefix)

**Error Handling:**
- Return 500 if unable to access the data directory or read files
- Return 500 if data files are corrupted or malformed

## `Scenarios`

### Interfaces

```python
Scenarios(scenarios=scenarios)
```

- @input `scenarios` - `List` of `Scenario` models
- @returns a `Scenarios` model class

### Use Cases

Models a list of scenarios (captured as their metadata).

### Build

Depends on `Scenario`

#### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- models.py <--
```

### Constraints

N/A

## `get_scenario`

### Interfaces

```python
get_scenario(scenario_id: str) --> Scenario
```

### Use Cases

Simple pass through of metadata for the `scenario_id` specified.

### Build

Depends on `Scenario`

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- handlers.py <--
```

### Constraints

Needs to be capable of reading either from local disk or from `s3` depending on whether `FishFlowData` points to an `s3` bucket or not. (`s3://` prefix)

**Error Handling:**
- Return 404 if the scenario_id does not exist
- Return 500 if unable to access the data directory or read files
- Return 500 if data files are corrupted or malformed

## `Scenario`

### Interfaces

```python
Scenario(**scenario)
```

- @input `scenario` - a `dict` with all of the components found in `Data.md:MetaDataSchema`

### Use Cases

Model of `Data.md:MetaDataSchema`

### Build

#### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- models.py <--
```

### Constraints

N/A

## `get_geometries`

### Interfaces

```python
get_geometries(scenario_id: str) --> Geometries
```

### Use Cases

Simple pass through of geojson for the `scenario_id` specified.

### Build

Depends on `Geometries`

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- handlers.py <--
```

### Constraints

Needs to be capable of reading either from local disk or from `s3` depending on whether `FishFlowData` points to an `s3` bucket or not. (`s3://` prefix)

**Error Handling:**
- Return 404 if the scenario_id does not exist
- Return 500 if unable to access the data directory or read files
- Return 500 if data files are corrupted or malformed

## `Geometries`

### Interfaces

```python
Geometries(geojson)
```

- @input `geojson` - geojson as defined in `Data.md:GeometriesSchema`

### Use Cases

Model of `Data.md:GeometriesSchema`

### Build

#### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- models.py <--
```

### Constraints

N/A

## `get_cell_depths`

### Interfaces

```python
get_cell_depths(scenario_id: str) --> CellDepths
```

### Use Cases

Simple pass through of cell_depths for the `scenario_id` specified.

### Build

Depends on `CellDepths`

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- handlers.py <--
```

### Constraints

Needs to be capable of reading either from local disk or from `s3` depending on whether `FishFlowData` points to an `s3` bucket or not. (`s3://` prefix)

**Error Handling:**
- Return 404 if the scenario_id does not exist
- Return 500 if unable to access the data directory or read files
- Return 500 if data files are corrupted or malformed

## `CellDepths`

### Interfaces

```python
CellDepths(cell_depths)
```

- @input `cell_depths` - a `dict` with all of the components found in `Data.md:CellDepthsSchema`

### Use Cases

Model of `Data.md:CellDepthsSchema

### Build

#### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- models.py <--
```

### Constraints

N/A

## `get_timestamps`

### Interfaces

```python
get_timestamps(scenario_id: str) --> Timestamps
```

### Use Cases

Simple pass through of timestamps for the `scenario_id` specified.

### Build

Depends on `Timestamps`

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- handlers.py <--
```

### Constraints

Needs to be capable of reading either from local disk or from `s3` depending on whether `FishFlowData` points to an `s3` bucket or not. (`s3://` prefix)

**Error Handling:**
- Return 404 if the scenario_id does not exist
- Return 500 if unable to access the data directory or read files
- Return 500 if data files are corrupted or malformed

## `Timestamps`

### Interfaces

```python
Timestamps(timestamps)
```

- @input `timestamps` - a `list` as defined in `Data.md:TimestampsSchema`

### Use Cases

Model of `Data.md:TimestampsSchema

### Build

#### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- models.py <--
```

### Constraints

N/A

## `get_minimums`

### Interfaces

```python
get_minimums(scenario_id: str) --> Minimums
```

### Use Cases

Simple pass through of minimums for the `scenario_id` specified.

### Build

Depends on `Minimums`

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- handlers.py <--
```

### Constraints

Needs to be capable of reading either from local disk or from `s3` depending on whether `FishFlowData` points to an `s3` bucket or not. (`s3://` prefix)

**Error Handling:**
- Return 404 if the scenario_id does not exist
- Return 500 if unable to access the data directory or read files
- Return 500 if data files are corrupted or malformed

## `Minimums`

### Interfaces

```python
Minimums(minimums)
```

- @input `minimums` - a `dict` with all of the components found in `Data.md:MinimumsSchema`

### Use Cases

Model of `Data.md:MinimumsSchema`

### Build

#### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- models.py <--
```

### Constraints

N/A

## `get_occupancy`

### Interfaces

```python
get_occupancy(scenario_id: str, cell_id: int, depth_bin: float) --> Occupancy
```

`cell_id` (int, required) and `depth_bin` (float, required) both come from query parameters in the endpoint URL.

Example: `/v1/depth/scenario/{scenario_id}/occupancy?cell_id=123&depth_bin=10.5`

### Use Cases

Pulls the timelines (as an array) for the `cell_id` and `depth_bin` in question. Note that because we have multiple models per report this will actually be an array of arrays:

`[model0_timeline, model1_timeline,..., modeln_timeline]`

See `Data.md:OccupancySchema` for details on the data structure that we are pulling from for this endpoint. See `Data.md:Overall Organization` for how the files are broken up between cell ids.

To translate the `depth_bin` float parameter to a `depth_bin_idx`, find the index of the depth_bin in the `depth_bins` array from the metadata (see `Data.md:MetaDataSchema`).

### Build

Depends on `Occupancy`

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- handlers.py <--
```

### Constraints

Needs to be capable of reading either from local disk or from `s3` depending on whether `FishFlowData` points to an `s3` bucket or not. (`s3://` prefix)

**Error Handling:**
- Return 404 if the scenario_id does not exist
- Return 404 if the parquet file for the specified cell_id does not exist (indicating the cell_id is invalid)
- Return 400 if cell_id or depth_bin query parameters are missing or invalid
- Return 400 if the depth_bin is not found in the scenario's depth_bins array
- Return 500 if unable to access the data directory or read files
- Return 500 if data files (including parquet files) are corrupted or malformed

## `Occupancy`

### Interfaces

```python
Occupancy(timelines)
```

- @input `timelines` - an array of likelihood timelines per model for a specific cell at a specific depth bin.

### Use Cases

Model of the timelines for one cell and depth bin from `Data.md:OccupancySchema`

### Build

#### Placement

```bash
fishflow
|
+-- backend
|   |
|   +-- api
|   |   |
|   |   +-- app
|   |   |   |
|   |   |   +-- depth
|   |   |   |   |
|   |   |   |   +-- models.py <--
```

### Constraints

N/A
