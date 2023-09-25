from unittest.mock import patch, Mock
from src.log_message import log_message
from botocore.exceptions import ClientError


FAKE_AWS_CREDENTIALS = {
    "aws_access_key_id": "fake_access_key",
    "aws_secret_access_key": "fake_secret_key",
    "aws_session_token": "fake_session_token",
}


@patch('src.log_message.boto3.client')
def test_log_message_with_registered_repo(mock_boto3_client):
    # Mock the head_object to simulate registered repo
    mock_boto3_client().head_object.return_value = {}

    result = log_message("registered_repo", {"event": "push"})
    assert result["status"] == "success"
    assert result["message"] == "Successfully logged event."


@patch('src.log_message.boto3.client')
def test_log_message_with_unregistered_repo(mock_boto3_client):
    # Mock the head_object to simulate unregistered repo (throwing a 404)
    mock_boto3_client().head_object.side_effect = Mock(side_effect=ClientError({
        'Error': {'Code': '404', 'Message': 'Not Found'}
    }, 'head_object'))

    result = log_message("unregistered_repo", {"event": "push"})
    assert result["status"] == "error"
    assert result["message"] == "Repository not registered, can't log event."


@patch('src.log_message.boto3.client')
def test_log_message_with_s3_error(mock_boto3_client):
    # Mock the head_object to simulate an S3 error other than 404
    mock_boto3_client().head_object.side_effect = Mock(side_effect=ClientError({
        'Error': {'Code': '500', 'Message': 'Internal Server Error'}
    }, 'head_object'))

    result = log_message("some_repo", {"event": "push"})
    assert result["status"] == "error"
    assert result["message"].startswith("An S3 error occurred:")
