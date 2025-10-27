## `TitleBar`
`fishflow_app/src/components/common/TitleBar.jsx`

```jsx
<TitleBar
  scenarioName={scenario.name}
  reportType="Depth Occupancy Report"
  onBack={onNavigate}
  onHome={onNavigate}
/>
```

- **@input** `scenarioName` - String name of the scenario being displayed
- **@input** `reportType` - String describing the type of report (e.g., "Depth Occupancy Report")
- **@input** `onBack` - Function callback for navigating back to report selection
- **@input** `onHome` - Function callback for navigating to home page

#### Notes

Displays the report title with scenario name and navigation buttons for going back to selection or returning home.

Should display as a horizontal bar containing:
- Report type and scenario name (left side)
- Navigation buttons (right side):
  - "Back to Selection" button
  - "Home" button
##### Styling

**Colors**
- Background: `#f8f9fa` (Bootstrap light grey)
- Text: `#212529`
- Border bottom: `1px solid #dee2e6`

**Layout**
- Display: flexbox with space-between justification
- Padding: `1rem 1.5rem`
- Width: 100% of parent container

**Typography**
- Report type font-size: `1.25rem` (20px)
- Report type font-weight: `500`
- Scenario name font-size: `1rem` (16px)
- Font family: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`

**Button Styling**
- Background: `#ffffff`
- Border: `1px solid #dee2e6`
- Border radius: `0.25rem`
- Padding: `0.5rem 1rem`
- Font size: `0.875rem`
- Color: `#212529`
- Cursor: `pointer`
- Hover: `rgba(13, 110, 253, 0.1)` background tint
- Transition: `all 0.15s ease-in-out`
- Margin-left between buttons: `0.5rem`

**Accessibility**
- Semantic HTML (`<header>` element)
- ARIA labels for navigation buttons
- Keyboard navigable