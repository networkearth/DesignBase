"""
FishFlow FastAPI Application.

Main application entry point that configures and registers all endpoints.
"""

from typing import Dict, Tuple, Callable, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import inspect

from app.depth import ENDPOINT_SPEC


def register_endpoint_spec(app: FastAPI, endpoint_spec: Dict[str, Tuple[Callable, Any]]) -> None:
    """
    Register endpoints from an endpoint specification.

    Given an endpoint_spec like:
    {
        "/v1/endpoint1": (endpoint_1, response_model1),
        "/v1/endpoint2/{param}": (endpoint_2, response_model2),
    }

    Registers the endpoint functions and response models with a FastAPI app as GET endpoints.
    All endpoints are registered as GET requests with a 200 status code on success.

    Args:
        app: FastAPI application instance
        endpoint_spec: Dictionary mapping URL paths to (handler_function, response_model) tuples
    """
    for path, (handler, response_model) in endpoint_spec.items():
        # Extract path parameters from the path string
        # e.g., "/v1/depth/scenario/{scenario_id}/scenario" -> ["scenario_id"]

        # Get the handler's signature to properly pass through all parameters
        sig = inspect.signature(handler)

        # Create a wrapper function that preserves the signature
        # This is necessary so FastAPI can properly extract path and query parameters
        def create_endpoint(handler_func, model):
            # Get parameters from handler signature
            params = sig.parameters

            # Build the wrapper function dynamically with the same signature
            async def endpoint(**kwargs):
                return handler_func(**kwargs)

            # Copy the signature to the wrapper
            endpoint.__signature__ = sig

            return endpoint

        wrapper = create_endpoint(handler, response_model)

        # Register the endpoint
        app.get(
            path,
            response_model=response_model,
            status_code=200,
        )(wrapper)


# Initialize FastAPI application
app = FastAPI(
    title="FishFlow API",
    description="API for serving data from behavioral models for the FishFlow App",
    version="1.0.0",
)

# Configure CORS to handle multiple allowed origins
# Support localhost for development and production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://networkearth.io",
        "https://www.networkearth.io",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Register depth endpoints
register_endpoint_spec(app, ENDPOINT_SPEC)


# Health check endpoint
@app.get("/health", status_code=200)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Dictionary with status "healthy" to indicate the API is running
    """
    return {"status": "healthy"}
