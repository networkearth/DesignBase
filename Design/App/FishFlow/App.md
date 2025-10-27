## `App`
`fishflow_app/src/App.js`

#### Notes

The main application component that sets up routing using React Router.
##### Routes

**Root Route (`/`):**
- Immediately redirects to `/depth_occupancy/example`
- Uses React Router's `Navigate` component with `replace` prop to avoid creating browser history entry
- Example: `<Navigate to="/depth_occupancy/example" replace />`

**Depth Occupancy Route (`/depth_occupancy/:scenario_id`):**
- Renders the `DepthOccupancyReport` page component
- `scenario_id` is a URL parameter accessible via `useParams()` hook
- Example: `/depth_occupancy/chinook_2022`
- Query parameters (months, hours, cell_id) are handled within the `DepthOccupancyReport` component

**404 Route (catch-all):**
- Any unmatched routes should redirect to `/depth_occupancy/example`
- Use `path="*"` to catch all unmatched routes

##### Implementation

Uses React Router v6 with the following structure:

##### Navigation Functions

The TitleBar component needs navigation callbacks. These should be passed from `DepthOccupancyReport` using the `useNavigate()` hook:

```jsx
const navigate = useNavigate();

// For "Back to Selection" - for now, just goes to home (same as onHome)
const handleBack = () => navigate('/depth_occupancy/example');

// For "Home" button
const handleHome = () => navigate('/depth_occupancy/example');
```

**Future Enhancement:** When a scenario selection page is added, `handleBack` should navigate to that page instead.

#### Dependencies

- `react-router-dom` (v6.20.0+)
- `DepthOccupancyReport` page component