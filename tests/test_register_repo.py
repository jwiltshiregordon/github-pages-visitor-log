import boto3
import pytest
from moto import mock_s3
from unittest.mock import patch
from src.register_repo import register_repo
from src.constants import CHALLENGE_FILENAME

FAKE_AWS_CREDENTIALS = {
    "aws_access_key_id": "fake_access_key",
    "aws_secret_access_key": "fake_secret_key",
    "aws_session_token": "fake_session_token",
}

@pytest.fixture
def s3():
    with mock_s3():
        conn = boto3.client("s3", **FAKE_AWS_CREDENTIALS)
        conn.create_bucket(Bucket="my_test_bucket")
        yield conn


@patch('src.register_repo.requests.get')
def test_register_repo_with_valid_file(mock_requests_get, s3):
    mock_requests_get.return_value.status_code = 200
    result = register_repo("some_repo_name", "some_repo_owner")
    assert result == "Successfully registered"
    mock_requests_get.assert_called_with(f"https://github.com/some_repo_owner/some_repo_name/blob/main/{CHALLENGE_FILENAME}")


@patch('src.register_repo.requests.get')
def test_register_repo_with_missing_file(mock_requests_get, s3):
    mock_requests_get.return_value.status_code = 404
    result = register_repo("some_repo_name", "some_repo_owner")
    assert result != "Successfully registered"
    mock_requests_get.assert_called_with(f"https://github.com/some_repo_owner/some_repo_name/blob/main/{CHALLENGE_FILENAME}")
