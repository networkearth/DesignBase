## `CheckBoxPicker`
`fishflow_app/src/components/common/CheckBoxPicker.jsx`

```jsx
<CheckBoxPicker
  labels={['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']}
  selected={selected}
  setSelected={setSelected}
  title="Select Months"
  size="medium"
  layout="horizontal"
  stacks={3}
  justify="center"
/>
```

- **@input** `labels` - Array of strings to display in each box (determines number of boxes)
- **@input** `selected` - Array of selected indices (0-based), sorted in ascending order
- **@input** `setSelected` - Setter function for `selected`
- **@style** `title` - Title text displayed above the picker (optional)
- **@style** `size` - `"small"` | `"medium"` | `"large"` - Controls text and box sizing; component fills parent container (default: `"medium"`)
- **@style** `layout` - `"horizontal"` | `"vertical"` - Determines primary direction of item arrangement (default: `"horizontal"`)
- **@style** `stacks` - Number of rows (horizontal layout) or columns (vertical layout) (required)
- **@style** `justify` - Alignment/distribution of boxes within the container (default: `"center"`):
  - Horizontal layout: `"left"` | `"right"` | `"center"`
  - Vertical layout: `"top"` | `"bottom"` | `"center"`
- **@affects** `selected`

#### Notes

When users click on a box that is not selected, `selected` should be updated to include that item's index. When users click on a box that is already selected, it should remove that index from `selected`.

There should be a box for each label in the `labels` array, set inside a container with a customizable title. Each box should display its corresponding label. When a box is selected, it should change color to indicate selection.
##### Styling

**Colors**
- Primary/Selected: `#0d6efd` (Bootstrap blue)
- Border: `#dee2e6`
- Text: `#212529`
- Background: `#ffffff`
- Hover: `rgba(13, 110, 253, 0.1)` background tint
- Focus: `0 0 0 0.25rem rgba(13, 110, 253, 0.25)` box shadow

**Size Variations**
- **Small**: 0.875rem (14px) font, 0.5rem padding
- **Medium** (default): 1rem (16px) font, 0.75rem padding
- **Large**: 1.25rem (20px) font, 1rem padding

**Box Styling**
- Border radius: `0.25rem`
- Border: `1px solid #dee2e6`
- Selected state: Background `#0d6efd`, white text
- Transition: `all 0.15s ease-in-out`
- Box dimensions determined by `size` parameter (not content-dependent)
- Boxes distribute within parent container according to `justify` parameter

**Spacing**
- Gap between boxes: 0.5rem (small/medium), 0.75rem (large)
- Title margin-bottom: 0.75rem

**Typography**
- Font family: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- Title font-weight: `500`

**Accessibility**
- Keyboard navigable
- Focus outline with box-shadow
- ARIA label on container using title prop
- Each box has `role="checkbox"` and `aria-checked` state

## `HourPicker`
`fishflow_app/src/components/common/HourPicker.jsx`

```jsx
<HourPicker
  selectedHours={selectedHours}
  setSelectedHours={setSelectedHours}
  title="Select Hours"
  size="medium"
  layout="horizontal"
  stacks={4}
  justify="center"
/>
```

- **@input** `selectedHours` - Array of selected hour numbers (0-23), sorted in ascending order
- **@input** `setSelectedHours` - Setter function for `selectedHours`
- **@style** `title` - Title text displayed above the hour picker (optional)
- **@style** `size` - `"small"` | `"medium"` | `"large"` (default: `"medium"`)
- **@style** `layout` - `"horizontal"` | `"vertical"` (default: `"horizontal"`)
- **@style** `stacks` - Number of rows (horizontal) or columns (vertical) (required)
- **@style** `justify` - `"left"` | `"right"` | `"center"` (horizontal) or `"top"` | `"bottom"` | `"center"` (vertical) (default: `"center"`)
- **@affects** `selectedHours`
#### Notes
A specialized wrapper around `CheckBoxPicker` configured for hour selection. Converts between hour numbers (0-23) and 0-based indices (0-23) for the underlying `CheckBoxPicker`.

Uses `CheckBoxPicker` with `labels` set to hour numbers `['0', '1', '2', ..., '23']`.

##### Constraints
- Hours (0-23) map directly to 0-based indices (0-23), so no conversion needed
- Simply passes through values to and from `CheckBoxPicker`
#### Dependencies 

- `CheckBoxPicker`

## `MonthPicker`
`fishflow_app/src/components/common/MonthPicker.jsx`

```jsx
<MonthPicker
  selectedMonths={selectedMonths}
  setSelectedMonths={setSelectedMonths}
  title="Select Months"
  size="medium"
  layout="horizontal"
  stacks={3}
  justify="center"
/>
```

- **@input** `selectedMonths` - Array of selected month numbers (1-12), sorted in ascending order
- **@input** `setSelectedMonths` - Setter function for `selectedMonths`
- **@style** `title` - Title text displayed above the month selector (optional)
- **@style** `size` - `"small"` | `"medium"` | `"large"` (default: `"medium"`)
- **@style** `layout` - `"horizontal"` | `"vertical"` (default: `"horizontal"`)
- **@style** `stacks` - Number of rows (horizontal) or columns (vertical) (required)
- **@style** `justify` - `"left"` | `"right"` | `"center"` (horizontal) or `"top"` | `"bottom"` | `"center"` (vertical) (default: `"center"`)
- **@affects** `selectedMonths`
#### Notes
A specialized wrapper around `CheckBoxPicker` configured for month selection. Converts between 1-based month numbers (1-12) and 0-based indices (0-11) for the underlying `CheckBoxPicker`.

Uses `CheckBoxPicker` with `labels` set to month abbreviations `['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']`.

##### Constraints
- Converts `selectedMonths` (1-12) to 0-based indices before passing to `CheckBoxPicker`
- Converts 0-based indices back to month numbers (1-12) when updating `selectedMonths`
#### Dependencies
- `CheckBoxPicker`


