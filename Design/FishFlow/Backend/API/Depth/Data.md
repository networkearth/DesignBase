This is just context, the actual data is placed by other components. 

## Overall Organization

```bash
+-- {scenario_id}
|   | 
|   +-- meta_data.json
|   +-- geometries.geojson
|   +-- cell_depths.json
|   +-- minimums.json
|   +-- timestamps.json
|   +-- {cell_id}_occupancy.parquet.gz
```

Given the `FishFlowData` parameter passed to the API this data will be stored in the `depth/` directory at that location. `FishFlowData` can refer either to an S3 bucket directory or a local directory. As such there is nothing to actually build here.

Note as a result of the above folder structure there is one subdirectory for each `scenario_id`.

## `MetaDataSchema`

- scenario_id: str
- name: str
- species: str
- model: str
- reference_model: str
- region: str
- reference_region: str
- description: str
- time_window: \[datetime, datetime] (format: "YYYY-MM-DD HH:MM:SS")
- reference_time_window: \[datetime, datetime] (format: "YYYY-MM-DD HH:MM:SS")
- grid_size: int
- depth_bins: \[float, float, ..., float]
- resolution: int
- support: \[float, float, ..., float]

## `GeometriesSchema`

Geojson of polygons with a `cell_id(int)` for each polygon. 

## `CellDepthsSchema`

`{cell_id(int) -> maximum_depth_bin(float)}`

## `MinimumsSchema`

`{cell_id(int) -> {depth_bin -> {month(int) -> minimums_array}}}`

`minimums_array` is the minimum depth occupancy in that cell and month per hour `0-23`. It is an array of length 24 containing floats.

## `TimestampsSchema`

An ordered array of all the timestamps in the report.

## OccupancySchema`

For a specific a `cell_id(int)` timelines for each model and depth bin. Models follow the same order as `support` (from `MetaDataSchema`) and depth bins follow the same order as `depth_bins` (also from `MetaDataSchema`). The rows of the parquet file follow the same order as the `timestamps.json`. For the columns we have `model_idx=col // num_depth_bins` and `depth_bin_idx=col % num_depth_bins`. The values are floats representing the likelihood of occupying that depth bin given the model in question. If the depth bin exceeds the maximum specified in `cell_depths.json` for this `cell_id(int)` then the column will be null. 

