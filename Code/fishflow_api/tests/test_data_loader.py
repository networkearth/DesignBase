"""Tests for data loading utilities."""

import pytest
import json
import os
from pathlib import Path
from app.data_loader import (
    is_s3_path,
    parse_s3_path,
    read_json_file,
    list_directories
)


class TestS3PathHandling:
    """Test S3 path detection and parsing."""

    def test_is_s3_path_true(self):
        """Test that S3 paths are correctly identified."""
        assert is_s3_path("s3://my-bucket/path/to/file") is True
        assert is_s3_path("s3://bucket") is True

    def test_is_s3_path_false(self):
        """Test that non-S3 paths are correctly identified."""
        assert is_s3_path("/local/path") is False
        assert is_s3_path("relative/path") is False
        assert is_s3_path("http://example.com") is False

    def test_parse_s3_path_with_key(self):
        """Test parsing S3 path with bucket and key."""
        bucket, key = parse_s3_path("s3://my-bucket/path/to/file")
        assert bucket == "my-bucket"
        assert key == "path/to/file"

    def test_parse_s3_path_bucket_only(self):
        """Test parsing S3 path with only bucket."""
        bucket, key = parse_s3_path("s3://my-bucket")
        assert bucket == "my-bucket"
        assert key == ""

    def test_parse_s3_path_invalid(self):
        """Test that invalid S3 paths raise ValueError."""
        with pytest.raises(ValueError):
            parse_s3_path("/local/path")


class TestLocalFileOperations:
    """Test local file system operations."""

    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Create temporary data directory structure."""
        # Create test directory structure
        depth_dir = tmp_path / "depth"
        depth_dir.mkdir()

        scenario1 = depth_dir / "scenario1"
        scenario2 = depth_dir / "scenario2"
        scenario1.mkdir()
        scenario2.mkdir()

        # Create test JSON file
        test_data = {"test": "data", "value": 123}
        json_file = scenario1 / "test.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)

        return tmp_path

    def test_read_json_file_local(self, temp_data_dir):
        """Test reading JSON file from local filesystem."""
        data = read_json_file(str(temp_data_dir), "depth/scenario1/test.json")
        assert data["test"] == "data"
        assert data["value"] == 123

    def test_read_json_file_not_found(self, temp_data_dir):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError):
            read_json_file(str(temp_data_dir), "depth/nonexistent/test.json")

    def test_read_json_file_invalid_json(self, temp_data_dir):
        """Test that ValueError is raised for invalid JSON."""
        # Create invalid JSON file
        invalid_file = temp_data_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json }")

        with pytest.raises(ValueError):
            read_json_file(str(temp_data_dir), "invalid.json")

    def test_list_directories_local(self, temp_data_dir):
        """Test listing directories from local filesystem."""
        dirs = list_directories(str(temp_data_dir), "depth")
        assert sorted(dirs) == ["scenario1", "scenario2"]

    def test_list_directories_empty(self, temp_data_dir):
        """Test listing directories when none exist."""
        empty_dir = temp_data_dir / "empty"
        empty_dir.mkdir()
        dirs = list_directories(str(temp_data_dir), "empty")
        assert dirs == []

    def test_list_directories_nonexistent(self, temp_data_dir):
        """Test listing directories for nonexistent path."""
        dirs = list_directories(str(temp_data_dir), "nonexistent")
        assert dirs == []
