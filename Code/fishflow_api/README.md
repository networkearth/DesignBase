# FishFlow API

A FastAPI application that serves data from behavioral models for the FishFlow App.

## Overview

The FishFlow API provides endpoints to access depth occupancy reports for various scenarios, including:
- Scenario metadata and listings
- Geographic geometries (GeoJSON)
- Cell depth mappings
- Timestamps
- Minimum occupancy data
- Occupancy timelines for specific cells and depth bins

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`

## Installation

1. **Clone or navigate to the repository:**
   ```bash
   cd fishflow_api
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The API requires environment variables to be set:

### Required Environment Variables

- **`FISHFLOW_DATA_DIR`**: Path to the data directory (local path or S3 URL)
  - Local example: `/path/to/data` or `./data`
  - S3 example: `s3://my-bucket/fishflow-data`

### Optional Environment Variables

- **`FISHFLOW_API_MODE`**: Set to `DEV` (default) for local development or `PROD` for production
  - `DEV`: Runs on `127.0.0.1:8000` with auto-reload
  - `PROD`: Runs on `0.0.0.0:8000` without auto-reload

### Example Configuration

```bash
# For local development with local data
export FISHFLOW_DATA_DIR="./data"
export FISHFLOW_API_MODE="DEV"

# For production with S3 data
export FISHFLOW_DATA_DIR="s3://fishflow-bucket/data"
export FISHFLOW_API_MODE="PROD"
```

## Running the API

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using the Python module directly:

```bash
python -m app.main
```

### Production Mode

```bash
export FISHFLOW_API_MODE="PROD"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: See `api.yaml` in the project root

## API Endpoints

### Health Check

- **GET** `/health` - Returns API health status

### Depth Endpoints

- **GET** `/v1/depth/scenario/scenarios` - List all available scenarios
- **GET** `/v1/depth/scenario/{scenario_id}/scenario` - Get scenario metadata
- **GET** `/v1/depth/scenario/{scenario_id}/geometries` - Get GeoJSON geometries
- **GET** `/v1/depth/scenario/{scenario_id}/cell_depths` - Get cell depth mappings
- **GET** `/v1/depth/scenario/{scenario_id}/timestamps` - Get timestamps array
- **GET** `/v1/depth/scenario/{scenario_id}/minimums` - Get minimum occupancy data
- **GET** `/v1/depth/scenario/{scenario_id}/occupancy?cell_id={cell_id}&depth_bin={depth_bin}` - Get occupancy timelines

## Data Structure

The API expects data to be organized as follows:

```
{FISHFLOW_DATA_DIR}/
└── depth/
    └── {scenario_id}/
        ├── meta_data.json
        ├── geometries.geojson
        ├── cell_depths.json
        ├── minimums.json
        ├── timestamps.json
        └── {cell_id}_occupancy.parquet.gz
```

### Data Files

- **`meta_data.json`**: Scenario metadata including depth bins, time windows, and model information
- **`geometries.geojson`**: GeoJSON FeatureCollection with polygon geometries and cell_id properties
- **`cell_depths.json`**: Mapping of cell_id to maximum depth bin
- **`timestamps.json`**: Ordered array of timestamps for the scenario
- **`minimums.json`**: Nested structure of minimum occupancy by cell, depth, month, and hour
- **`{cell_id}_occupancy.parquet.gz`**: Compressed Parquet file containing occupancy timelines

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestHealthCheck::test_health_check
```

## Example Usage

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# List scenarios
curl http://localhost:8000/v1/depth/scenario/scenarios

# Get scenario metadata
curl http://localhost:8000/v1/depth/scenario/test_scenario_1/scenario

# Get occupancy for specific cell and depth
curl "http://localhost:8000/v1/depth/scenario/test_scenario_1/occupancy?cell_id=123&depth_bin=10.5"
```

### Using Python

```python
import requests

# Base URL
base_url = "http://localhost:8000"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# Get all scenarios
response = requests.get(f"{base_url}/v1/depth/scenario/scenarios")
scenarios = response.json()["scenarios"]
print(f"Found {len(scenarios)} scenarios")

# Get specific scenario
scenario_id = scenarios[0]["scenario_id"]
response = requests.get(f"{base_url}/v1/depth/scenario/{scenario_id}/scenario")
metadata = response.json()
print(f"Scenario: {metadata['name']}")

# Get occupancy data
params = {"cell_id": 123, "depth_bin": 10.0}
response = requests.get(
    f"{base_url}/v1/depth/scenario/{scenario_id}/occupancy",
    params=params
)
occupancy = response.json()
print(f"Received {len(occupancy['timelines'])} model timelines")
```

## Error Handling

The API returns standard HTTP status codes:

- **200**: Success
- **400**: Bad request (invalid parameters)
- **404**: Not found (scenario, file, or data not found)
- **422**: Validation error (missing or invalid query parameters)
- **500**: Server error (corrupt data, configuration issues, or internal errors)

Error responses include a `detail` field with a descriptive message:

```json
{
  "detail": "Scenario 'invalid_id' not found"
}
```

## AWS S3 Configuration

When using S3 for data storage (`FISHFLOW_DATA_DIR` starts with `s3://`), ensure:

1. AWS credentials are configured (via environment variables, AWS CLI, or IAM roles)
2. The application has read access to the specified S3 bucket
3. Required environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION` (optional)

Or use IAM roles if running on AWS infrastructure (EC2, ECS, Lambda, etc.).

## Project Structure

```
fishflow_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and endpoints
│   ├── data_loader.py       # Data loading utilities (local + S3)
│   └── depth/
│       ├── __init__.py
│       ├── handlers.py      # Business logic for depth endpoints
│       └── models.py        # Pydantic models for responses
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # Integration tests
│   └── test_data_loader.py  # Unit tests for data loading
├── api.yaml                 # OpenAPI specification
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
└── README.md               # This file
```

## Development

### Adding New Endpoints

1. Define Pydantic models in `app/depth/models.py`
2. Implement handler logic in `app/depth/handlers.py`
3. Register endpoint in `app/main.py`
4. Update `api.yaml` with endpoint documentation
5. Add tests in `tests/test_api.py`

### Code Quality

The codebase follows these practices:
- Type hints for all function parameters and return values
- Comprehensive docstrings (Google style)
- Input validation and defensive programming
- Clear, descriptive error messages
- Separation of concerns (models, handlers, data loading)

## Deployment

### Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV FISHFLOW_API_MODE=PROD
ENV FISHFLOW_DATA_DIR=/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t fishflow-api .
docker run -p 8000:8000 -e FISHFLOW_DATA_DIR=/data -v /path/to/data:/data fishflow-api
```

## License

[Your License Here]

## Support

For issues, questions, or contributions, please contact the development team.
