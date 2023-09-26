import json
from unittest.mock import patch, Mock

import boto3
import pytest
from moto import mock_s3

from src.constants import NOT_REGISTERED, REGISTERED_PATH, LOGS_PATH, AWS_S3_BUCKET
from src.log_message import log_message
from botocore.exceptions import ClientError

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


@patch('src.log_message.boto3.client')
def test_log_message_with_unregistered_repo(mock_boto3_client):
    # Mock the head_object to simulate unregistered repo (throwing a 404)
    mock_boto3_client().head_object.side_effect = Mock(side_effect=ClientError({
        'Error': {'Code': '404', 'Message': 'Not Found'}
    }, 'head_object'))

    result = log_message("owner", "unregistered_repo", {"event": "push"})
    assert result["status"] == "error"
    assert result["message"] == NOT_REGISTERED


@patch('src.log_message.boto3.client')
def test_log_message_with_s3_error(mock_boto3_client):
    # Mock the head_object to simulate an S3 error other than 404
    mock_boto3_client().head_object.side_effect = Mock(side_effect=ClientError({
        'Error': {'Code': '500', 'Message': 'Internal Server Error'}
    }, 'head_object'))

    result = log_message('some_owner', "some_repo", {"event": "push"})
    assert result["status"] == "error"
    assert result["message"].startswith("An S3 error occurred:")


@patch('src.register_repo.requests.get')
def test_log_message_valid_registration(mock_requests_get, s3):
    mock_requests_get.return_value.status_code = 200
    register_repo("some_repo_owner", "some_repo_name")

    # Test the log_message function
    result = log_message("some_repo_owner", "some_repo_name", "Test message 1")
    assert result["status"] == "logged"

    # Check if next_key has been updated
    registered_key = f"{REGISTERED_PATH}some_repo_owner/some_repo_name"
    reg_object = s3.get_object(Bucket="my_test_bucket", Key=registered_key)
    reg_data = json.load(reg_object['Body'])
    assert reg_data["next_key"] == 1

    # Check if log message is correctly stored
    log_key = f"{LOGS_PATH}some_repo_owner/some_repo_name/00"
    log_data = json.loads(s3.get_object(Bucket="my_test_bucket", Key=log_key)['Body'].read().decode('utf-8'))
    assert log_data["event_details"] == "Test message 1"
