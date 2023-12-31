import json

import boto3
import pytest
from moto import mock_s3
from unittest.mock import patch
from src.register_repo import register_repo
from src.constants import AWS_S3_BUCKET, CHALLENGE_FILENAME, REGISTERED_PATH

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
def test_register_repo_with_valid_file(mock_requests_get, s3):
    mock_requests_get.return_value.status_code = 200
    result = register_repo("some_repo_owner", "some_repo_name")
    assert result["status"] == "registered"

    registered_key = f"{REGISTERED_PATH}some_repo_owner/some_repo_name"
    reg_object = s3.get_object(Bucket=AWS_S3_BUCKET, Key=registered_key)
    reg_data = json.load(reg_object['Body'])
    assert reg_data["next_key"] == 0


@patch('src.register_repo.requests.get')
def test_register_repo_with_missing_file(mock_requests_get, s3):
    mock_requests_get.return_value.status_code = 404
    result = register_repo("some_repo_owner", "some_repo_name")
    assert result['status'] == 'unregistered'

    mock_requests_get.assert_any_call(
        f"https://github.com/some_repo_owner/some_repo_name/blob/main/{CHALLENGE_FILENAME}")
    mock_requests_get.assert_any_call(
        f"https://github.com/some_repo_owner/some_repo_name/blob/master/{CHALLENGE_FILENAME}")

    response = s3.list_objects_v2(Bucket=AWS_S3_BUCKET, Prefix='registered/some_repo_name')
    assert 'Contents' not in response
