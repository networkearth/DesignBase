# FishFlow Backend API

FastAPI application that serves data from behavioral models for the FishFlow App.

## Overview

The FishFlow API provides endpoints for querying depth-related scenario data, including:
- Scenario metadata
- Geographic geometries (GeoJSON)
- Cell depth mappings
- Timestamps
- Minimum occupancy values
- Occupancy timelines by cell and depth

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository and navigate to the API directory:
```bash
cd Code/fishflow/backend/api
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Set the `FishFlowData` environment variable to point to your data directory:

### Local Development
```bash
export FishFlowData="/path/to/local/data"
```

### Production (S3)
```bash
export FishFlowData="s3://your-bucket-name/path/to/data"
```

The data directory should contain a `depth/` subdirectory with scenario data organized as follows:
```
depth/
├── scenario_id_1/
│   ├── meta_data.json
│   ├── geometries.geojson
│   ├── cell_depths.json
│   ├── minimums.json
│   ├── timestamps.json
│   └── {cell_id}_occupancy.parquet.gz
└── scenario_id_2/
    └── ...
```

### Development Mode

Set `FishFlowMode=dev` for local development:
```bash
export FishFlowMode=dev
```

## Running the API

### Development Server

Start the API with auto-reload enabled:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

The API will be available at:
- http://localhost:3000
- API documentation: http://localhost:3000/docs
- Alternative docs: http://localhost:3000/redoc

### Production Server

For production deployment:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000 --workers 4
```

## API Endpoints

### Health Check
- `GET /health` - Returns API health status

### Scenarios
- `GET /v1/depth/scenario/scenarios` - List all available scenarios
- `GET /v1/depth/scenario/{scenario_id}/scenario` - Get metadata for a specific scenario

### Scenario Data
- `GET /v1/depth/scenario/{scenario_id}/geometries` - Get GeoJSON geometries
- `GET /v1/depth/scenario/{scenario_id}/cell_depths` - Get cell depth mappings
- `GET /v1/depth/scenario/{scenario_id}/timestamps` - Get ordered timestamps
- `GET /v1/depth/scenario/{scenario_id}/minimums` - Get minimum occupancy values
- `GET /v1/depth/scenario/{scenario_id}/occupancy?cell_id={cell_id}&depth_bin={depth_bin}` - Get occupancy timelines

### Example Usage

```bash
# Check API health
curl http://localhost:3000/health

# List all scenarios
curl http://localhost:3000/v1/depth/scenario/scenarios

# Get scenario metadata
curl http://localhost:3000/v1/depth/scenario/my_scenario/scenario

# Get occupancy data for a specific cell and depth
curl "http://localhost:3000/v1/depth/scenario/my_scenario/occupancy?cell_id=123&depth_bin=10.5"
```

## Error Handling

The API returns standard HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Resource not found (scenario or cell does not exist)
- `500` - Server error (data access issues, malformed files)

Error responses include a detail message explaining the issue:
```json
{
  "detail": "Scenario 'invalid_id' not found"
}
```

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (development)
- `https://networkearth.io` (production)
- `https://www.networkearth.io` (production)

## Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Project Structure

```
backend/api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and endpoint registration
│   └── depth/
│       ├── __init__.py
│       ├── endpoints.py     # Endpoint specification (ENDPOINT_SPEC)
│       ├── handlers.py      # Handler functions for each endpoint
│       ├── models.py        # Pydantic response models
│       └── data_access.py   # Utilities for reading from S3/local filesystem
├── tests/
│   ├── __init__.py
│   ├── test_handlers.py
│   └── test_integration.py
├── requirements.txt
└── README.md
```

## Assumptions and Design Decisions

1. **Error Handling**: When listing scenarios, corrupted scenario directories are skipped rather than causing the entire request to fail. This allows the API to remain functional even if some data is malformed.

2. **Data Types**: All dictionary keys in JSON responses are converted to strings for consistency, even when they represent numeric IDs.

3. **S3 Integration**: boto3 is used for S3 access. The API determines whether to use S3 or local filesystem based on the `s3://` prefix in `FishFlowData`.

4. **Null Values**: Occupancy timelines may contain null values for depth bins that exceed the maximum depth for a given cell.

5. **Query Parameters**: The occupancy endpoint requires both `cell_id` and `depth_bin` as query parameters. These are validated before processing.

6. **CORS**: The API allows cross-origin requests from specified domains to support web-based frontends.

## Deployment

The API is designed to be deployed using Docker and AWS ECS with an Application Load Balancer (ALB) and Route53. See the infrastructure documentation for deployment details.

For local testing, the API can be run directly with uvicorn as shown in the "Running the API" section above.
