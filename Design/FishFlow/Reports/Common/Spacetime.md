## `build_geojson_h3`

### Interfaces

```python
build_geojson_h3(context_df) --> geojson, cell_id_df
```

- **@input** `context_df` - having at least the columns `_decision`, `_choice` (keys) and `h3_index`
- **@returns** `geojson` - a geojson of h3 polygons corresponding to each distinct `h3_index` and a `cell_id(int)` per polygon
- **@returns** `cell_id_df` - a dataframe with the columns `_decision`, `_choice`, `cell_id` where the `cell_id` corresponds to the original `h3_index` for this decision and choice. `cell_id`'s should start at 0 and rise from there (integer type)
### Use Cases

Builds a geojson from our context for each of the choices
### Build

#### Placement 

```bash
fishflow
|
+-- reports
|   |
|   +-- fishflow
|   |   |
|   |   +-- common
|   |   |   |
|   |   |   +-- spacetime.py <--
```

### Constraints

`cell_id`'s should be in the same order as the `h3_index`'s in alphabetical order

## `build_timeline`

### Interfaces

```python
build_timeline(context_df) --> timeline
```

- @input** `context_df` - having at least the columns `_decision`, `_choice` (keys) and `datetime`
- **@returns** `timeline` - an array (in order) of the unique `datetime`'s

### Use Cases

Pull the timeline from our context df
### Build
#### Placement 

```bash
fishflow
|
+-- reports
|   |
|   +-- fishflow
|   |   |
|   |   +-- common
|   |   |   |
|   |   |   +-- spacetime.py <--
```
### Constraints

Use `h3.cell_to_boundary`