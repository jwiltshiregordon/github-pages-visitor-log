import boto3
import pytest
from moto import mock_s3
from unittest.mock import patch
from src.register_repo import register_repo



@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    return {
        "aws_access_key_id": "testing",
        "aws_secret_access_key": "testing",
        "aws_session_token": "testing",
    }


@pytest.fixture
def s3(aws_credentials):
    with mock_s3():
        conn = boto3.client("s3", **aws_credentials)
        yield conn




@patch('src.register_repo.requests.get')
@patch('src.register_repo.boto3.client')
def test_register_repo(mock_boto3_client, mock_requests_get):
    mock_requests_get.return_value.status_code = 200

    result = register_repo("some_repo_name", "some_repo_owner")

    assert result == "Successfully registered"

