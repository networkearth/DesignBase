"""Data loading utilities for local and S3 storage.

This module provides functions to read data from either local filesystem
or S3 buckets, depending on the FISHFLOW_DATA_DIR configuration.
"""

import os
import json
from typing import Any, Dict, List
from pathlib import Path
import pandas as pd
import boto3
from io import BytesIO


def is_s3_path(path: str) -> bool:
    """Check if a path points to S3.

    Args:
        path: Path string to check

    Returns:
        True if path starts with 's3://', False otherwise
    """
    return path.startswith("s3://")


def parse_s3_path(s3_path: str) -> tuple[str, str]:
    """Parse S3 path into bucket and key.

    Args:
        s3_path: S3 path in format 's3://bucket/key/path'

    Returns:
        Tuple of (bucket_name, key_path)

    Raises:
        ValueError: If path is not a valid S3 path
    """
    if not is_s3_path(s3_path):
        raise ValueError(f"Not a valid S3 path: {s3_path}")

    path_without_prefix = s3_path[5:]  # Remove 's3://'
    parts = path_without_prefix.split('/', 1)

    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def read_json_file(base_path: str, relative_path: str) -> Dict[str, Any]:
    """Read JSON file from local or S3 storage.

    Args:
        base_path: Base directory path (local or S3)
        relative_path: Relative path to the JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid
        Exception: For S3-related errors
    """
    if is_s3_path(base_path):
        bucket, key_prefix = parse_s3_path(base_path)
        full_key = f"{key_prefix}/{relative_path}" if key_prefix else relative_path

        s3_client = boto3.client('s3')
        try:
            response = s3_client.get_object(Bucket=bucket, Key=full_key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found: s3://{bucket}/{full_key}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in s3://{bucket}/{full_key}: {e}")
    else:
        # Local file system
        full_path = Path(base_path) / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        try:
            with open(full_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {full_path}: {e}")


def read_geojson_file(base_path: str, relative_path: str) -> Dict[str, Any]:
    """Read GeoJSON file from local or S3 storage.

    GeoJSON files are just JSON files, so this is an alias for read_json_file.

    Args:
        base_path: Base directory path (local or S3)
        relative_path: Relative path to the GeoJSON file

    Returns:
        Parsed GeoJSON data as dictionary
    """
    return read_json_file(base_path, relative_path)


def read_parquet_file(base_path: str, relative_path: str) -> pd.DataFrame:
    """Read Parquet file from local or S3 storage.

    Args:
        base_path: Base directory path (local or S3)
        relative_path: Relative path to the Parquet file

    Returns:
        DataFrame containing the parquet data

    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: For S3-related or parquet reading errors
    """
    if is_s3_path(base_path):
        bucket, key_prefix = parse_s3_path(base_path)
        full_key = f"{key_prefix}/{relative_path}" if key_prefix else relative_path

        s3_client = boto3.client('s3')
        try:
            response = s3_client.get_object(Bucket=bucket, Key=full_key)
            content = response['Body'].read()
            return pd.read_parquet(BytesIO(content))
        except s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found: s3://{bucket}/{full_key}")
    else:
        # Local file system
        full_path = Path(base_path) / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        return pd.read_parquet(full_path)


def list_directories(base_path: str, relative_path: str = "") -> List[str]:
    """List directories in the given path.

    Args:
        base_path: Base directory path (local or S3)
        relative_path: Relative path to list directories from

    Returns:
        List of directory names (not full paths)

    Raises:
        Exception: For S3-related errors or file system errors
    """
    if is_s3_path(base_path):
        bucket, key_prefix = parse_s3_path(base_path)
        full_prefix = f"{key_prefix}/{relative_path}" if key_prefix else relative_path
        if full_prefix and not full_prefix.endswith('/'):
            full_prefix += '/'

        s3_client = boto3.client('s3')
        paginator = s3_client.get_paginator('list_objects_v2')

        # Use delimiter to get only immediate subdirectories
        directories = set()
        for page in paginator.paginate(Bucket=bucket, Prefix=full_prefix, Delimiter='/'):
            if 'CommonPrefixes' in page:
                for prefix in page['CommonPrefixes']:
                    # Extract just the directory name
                    dir_path = prefix['Prefix'].rstrip('/')
                    dir_name = dir_path.split('/')[-1]
                    directories.add(dir_name)

        return sorted(list(directories))
    else:
        # Local file system
        full_path = Path(base_path) / relative_path if relative_path else Path(base_path)
        if not full_path.exists():
            return []

        return sorted([d.name for d in full_path.iterdir() if d.is_dir()])
