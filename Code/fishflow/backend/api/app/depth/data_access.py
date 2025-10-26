"""
Data access utilities for reading from local filesystem or S3.

Provides unified interface for accessing data regardless of storage location.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd
from fastapi import HTTPException


def get_data_root() -> str:
    """
    Get the root directory for FishFlow data.

    Returns:
        Path to the data root (local or S3)

    Raises:
        HTTPException: If FishFlowData environment variable is not set
    """
    data_root = os.environ.get("FishFlowData")
    if not data_root:
        raise HTTPException(
            status_code=500,
            detail="FishFlowData environment variable not set"
        )
    return data_root


def is_s3_path(path: str) -> bool:
    """
    Check if a path points to S3.

    Args:
        path: Path to check

    Returns:
        True if path starts with 's3://', False otherwise
    """
    return path.startswith("s3://")


def list_directories(base_path: str) -> List[str]:
    """
    List all directories in the given base path.

    Works with both local filesystem and S3.

    Args:
        base_path: Path to search for directories

    Returns:
        List of directory names (not full paths)

    Raises:
        HTTPException: If unable to list directories
    """
    depth_path = os.path.join(base_path, "depth")

    if is_s3_path(base_path):
        try:
            import boto3
            from botocore.exceptions import ClientError

            # Parse S3 path
            s3_path = depth_path.replace("s3://", "")
            bucket_name = s3_path.split("/")[0]
            prefix = "/".join(s3_path.split("/")[1:])
            if prefix and not prefix.endswith("/"):
                prefix += "/"

            s3_client = boto3.client("s3")

            # List objects with the prefix
            paginator = s3_client.get_paginator("list_objects_v2")
            directories = set()

            for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter="/"):
                # CommonPrefixes contains the "directories"
                for common_prefix in page.get("CommonPrefixes", []):
                    dir_path = common_prefix["Prefix"]
                    # Extract just the directory name
                    dir_name = dir_path.rstrip("/").split("/")[-1]
                    directories.add(dir_name)

            return sorted(list(directories))

        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unable to access S3 data directory: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing S3 directories: {str(e)}"
            )
    else:
        try:
            path_obj = Path(depth_path)
            if not path_obj.exists():
                raise HTTPException(
                    status_code=500,
                    detail=f"Data directory does not exist: {depth_path}"
                )

            directories = [d.name for d in path_obj.iterdir() if d.is_dir()]
            return sorted(directories)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unable to list directories: {str(e)}"
            )


def read_json_file(base_path: str, scenario_id: str, filename: str) -> Dict[str, Any]:
    """
    Read a JSON file for a given scenario.

    Args:
        base_path: Root data path
        scenario_id: Scenario identifier
        filename: Name of the JSON file (e.g., 'meta_data.json')

    Returns:
        Parsed JSON data as dictionary

    Raises:
        HTTPException: If file cannot be read or parsed
    """
    file_path = os.path.join(base_path, "depth", scenario_id, filename)

    if is_s3_path(base_path):
        try:
            import boto3
            from botocore.exceptions import ClientError

            # Parse S3 path
            s3_path = file_path.replace("s3://", "")
            bucket_name = s3_path.split("/")[0]
            key = "/".join(s3_path.split("/")[1:])

            s3_client = boto3.client("s3")

            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=key)
                content = response["Body"].read().decode("utf-8")
                return json.loads(content)
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    raise HTTPException(
                        status_code=404,
                        detail=f"Scenario '{scenario_id}' not found"
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Unable to read file from S3: {str(e)}"
                    )

        except HTTPException:
            raise
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Malformed JSON in {filename}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading S3 file: {str(e)}"
            )
    else:
        try:
            path_obj = Path(file_path)

            if not path_obj.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario '{scenario_id}' not found"
                )

            with open(path_obj, "r") as f:
                return json.load(f)

        except HTTPException:
            raise
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Malformed JSON in {filename}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unable to read file: {str(e)}"
            )


def read_geojson_file(base_path: str, scenario_id: str) -> Dict[str, Any]:
    """
    Read a GeoJSON file for a given scenario.

    Args:
        base_path: Root data path
        scenario_id: Scenario identifier

    Returns:
        Parsed GeoJSON data as dictionary

    Raises:
        HTTPException: If file cannot be read or parsed
    """
    return read_json_file(base_path, scenario_id, "geometries.geojson")


def read_parquet_file(base_path: str, scenario_id: str, cell_id: int) -> pd.DataFrame:
    """
    Read a parquet file for a given scenario and cell.

    Args:
        base_path: Root data path
        scenario_id: Scenario identifier
        cell_id: Cell identifier

    Returns:
        DataFrame containing occupancy data

    Raises:
        HTTPException: If file cannot be read or parsed
    """
    filename = f"{cell_id}_occupancy.parquet.gz"
    file_path = os.path.join(base_path, "depth", scenario_id, filename)

    if is_s3_path(base_path):
        try:
            import boto3
            from botocore.exceptions import ClientError
            import io

            # Parse S3 path
            s3_path = file_path.replace("s3://", "")
            bucket_name = s3_path.split("/")[0]
            key = "/".join(s3_path.split("/")[1:])

            s3_client = boto3.client("s3")

            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=key)
                content = response["Body"].read()

                # Read parquet from bytes
                df = pd.read_parquet(io.BytesIO(content))
                return df

            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    raise HTTPException(
                        status_code=404,
                        detail=f"Cell ID {cell_id} not found for scenario '{scenario_id}'"
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Unable to read parquet file from S3: {str(e)}"
                    )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading S3 parquet file: {str(e)}"
            )
    else:
        try:
            path_obj = Path(file_path)

            if not path_obj.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Cell ID {cell_id} not found for scenario '{scenario_id}'"
                )

            df = pd.read_parquet(path_obj)
            return df

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Malformed or corrupted parquet file: {str(e)}"
            )
