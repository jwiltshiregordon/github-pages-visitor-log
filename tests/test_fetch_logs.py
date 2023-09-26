import boto3
import pytest
from moto import mock_s3
from unittest.mock import patch

from src.fetch_logs import fetch_logs
from src.log_message import log_message
from src.constants import AWS_S3_BUCKET
from src.register_repo import register_repo

FAKE_AWS_CREDENTIALS = {
    "aws_access_key_id": "fake_access_key",
    "aws_secret_access_key": "fake_secret_key",
    "aws_session_token": "fake_session_token",
}


@pytest.fixture
def s3():
    with mock_s3():
        conn = boto3.client("s3", **FAKE_AWS_CREDENTIALS)
        conn.create_bucket(Bucket=AWS_S3_BUCKET)
        yield conn


@patch('src.register_repo.requests.get')
def test_fetch_logs_valid_registration(mock_requests_get, s3):
    mock_requests_get.return_value.status_code = 200
    result = register_repo("some_repo_owner", "some_repo_name")
    assert result["status"] == "registered"

    # Log some messages
    log_message("some_repo_owner", "some_repo_name", "Test message 1")
    log_message("some_repo_owner", "some_repo_name", "Test message 2")

    # Fetch logs and verify
    result = fetch_logs("some_repo_owner", "some_repo_name")

    assert result["status"] == "success"
    print(result)
    assert [entry["event_details"] for entry in result["logs"]] == ["Test message 2", "Test message 1"]
