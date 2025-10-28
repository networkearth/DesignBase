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
- zoom: integer
- center: (lon, lat)

## `GeometriesSchema`

Geojson of polygons with a `cell_id(int)` for each polygon. 

Example: 
```
{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-87.9791261523691, 27.133982787018255], [-87.91310455101538, 27.202225741745043], [-87.9435487128635, 27.29035680823057], [-88.0401758616804, 27.31027933508803], [-88.10627060449633, 27.24197482771306], [-88.07566514853607, 27.15380941047907], [-87.9791261523691, 27.133982787018255]]]}, "properties": {"cell_id": 0}}, {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-88.01462137881663, 26.977524020246257], [-87.94868473388547, 27.045857124904842], [-87.9791261523691, 27.133982787018255], [-88.07566514853607, 27.15380941047907], [-88.14167455711748, 27.085414322960585], [-88.11107229751548, 26.997254659518514], [-88.01462137881663, 26.977524020246257]]]}, "properties": {"cell_id": 1}}, {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-87.85238269324536, 27.026009100730825], [-87.78643474701796, 27.09419041794012], [-87.81671509683717, 27.182281332552133], [-87.91310455101538, 27.202225741745043], [-87.9791261523691, 27.133982787018255], [-87.94868473388547, 27.045857124904842], [-87.85238269324536, 27.026009100730825]]]}, "properties": {"cell_id": 2}}, {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-87.88796809597541, 26.869653465693975], [-87.82210472816921, 26.937924501342568], [-87.85238269324536, 27.026009100730825], [-87.94868473388547, 27.045857124904842], [-88.01462137881663, 26.977524020246257], [-87.98418279558882, 26.8894050250461], [-87.88796809597541, 26.869653465693975]]]}, "properties": {"cell_id": 3}}]}
```

## `CellDepthsSchema`

`{cell_id(int) -> maximum_depth_bin(float)}`

## `MinimumsSchema`

`{cell_id(int) -> {depth_bin -> {month(int) -> minimums_array}}}`

`minimums_array` is the minimum depth occupancy in that cell and month per hour `0-23`. It is an array of length 24 containing floats. Months should run from `1-12`. 

## `TimestampsSchema`

An ordered array of all the timestamps in the report.

## OccupancySchema`

For a specific a `cell_id(int)` timelines for each model and depth bin. Models follow the same order as `support` (from `MetaDataSchema`) and depth bins follow the same order as `depth_bins` (also from `MetaDataSchema`). The rows of the parquet file follow the same order as the `timestamps.json`. For the columns we have `model_idx=col // num_depth_bins` and `depth_bin_idx=col % num_depth_bins`. The values are floats representing the likelihood of occupying that depth bin given the model in question. If the depth bin exceeds the maximum specified in `cell_depths.json` for this `cell_id(int)` then the column will be null. 

