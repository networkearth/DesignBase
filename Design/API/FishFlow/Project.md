## Summary
A `FastAPI` application that serves data from behavioral models for the `FishFlow` App.

```python
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Roots
```bash
http://localhost:8000
https://networkearth.io
https://www.networkearth.io
```

## Config

#### Environment Variables
- `FISHFLOW_API_MODE` - `DEV` or `PROD`, indicates whether the app should be run for local development (and use `http://localhost:8000`) or not
- `FISHFLOW_DATA_DIR` - either an `s3://` url or a local directory (can be relative) where the data this API is pulling is stored
## Structure
```bash
fishflow_api/
+-- requirements.txt
+-- api.yaml
+-- app/
|   +-- __init__.py
|   +-- main.py
|   +-- depth/
|   |   +-- __init__.py
|   |   +-- handlers.py
|   |   +-- models.py
+-- tests/
```

## Stack
```bash
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pandas==2.1.3
pyarrow==14.0.1
boto3==1.29.7
python-multipart==0.0.6
pytest==7.4.3
pytest-cov==4.1.0
httpx==0.25.1
```

## Tests
Should be selected and added by the LLM. 
## Health Check
`/health` should return a 200 all okay if the API is up and happy. 
## API Spec
An OpenAPI spec should be placed at `fishflow_api/api.yaml`.
## Further Designs
- `Depth/`
