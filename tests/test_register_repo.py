import boto3
import pytest
from moto import mock_s3
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


def test_register_repo(s3):
    # Given
    s3.create_bucket(Bucket="my_test_bucket")
    repo_name = "my_test_repo"
    
    # When
    register_repo(repo_name)
    
    # Then
    s3_objects = s3.list_objects_v2(Bucket="my_test_bucket")
    assert "Contents" in s3_objects
    assert len(s3_objects["Contents"]) == 2  # Change this based on how many documents you expect

    expected_keys = {f"registered/{repo_name}", f"logs/{repo_name}"}
    actual_keys = {obj["Key"] for obj in s3_objects["Contents"]}

    assert expected_keys.issubset(actual_keys)
