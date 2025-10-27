## `build_geojson_h3`
`fishflow/common/spacetime.py`

```python
build_geojson_h3(context_df) --> geojson, cell_id_df
```
#### Inputs
- `context_df` - `pd.DataFrame` having at least the columns `_decision`, `_choice` (keys) and `h3_index`
#### Outputs
- `geojson` - a geojson of h3 polygons corresponding to each distinct `h3_index` and a `cell_id(int)` per polygon
- `cell_id_df` - a `pd.DataFrame` with the columns `_decision`, `_choice`, `cell_id` where the `cell_id` corresponds to the original `h3_index` for this decision and choice. `cell_id`'s should start at 0 and rise from there (integer type)
#### Notes
`cell_id`'s should be in the same order as the `h3_index`'s in alphabetical order

Use `h3.cell_to_boundary`

## `build_timeline`
`fishflow/common/spacetime.py`

```python
build_timeline(context_df) --> timeline
```
#### Inputs
- `context_df` - a `pd.DataFrame` having at least the columns `_decision`, `_choice` (keys) and `datetime`
#### Outputs
- `timeline` - an array (in order) of the unique `datetime`'s
#### Notes

Pull the timeline from our context df.

