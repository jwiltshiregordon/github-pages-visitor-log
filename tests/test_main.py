import boto3
import pytest
from unittest.mock import patch

from moto import mock_s3

from src.constants import AWS_S3_BUCKET
from src.main import app

FAKE_AWS_CREDENTIALS = {
    "aws_access_key_id": "fake_access_key",
    "aws_secret_access_key": "fake_secret_key",
    "aws_session_token": "fake_session_token",
}


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def mock_s3_client():
    with mock_s3():
        conn = boto3.client("s3", **FAKE_AWS_CREDENTIALS)
        conn.create_bucket(Bucket=AWS_S3_BUCKET)
        yield boto3.client('s3', region_name='us-east-1')


@pytest.fixture
def setup_requests():
    with patch('requests.get') as mock_get:
        yield mock_get


def test_full_workflow(client, mock_s3_client, setup_requests):
    # Step 1: Register repo
    setup_requests.return_value.status_code = 200  # Simulate that sentinel file exists
    response = client.post('/register', json={'repo_name': 'some_repo_name', 'repo_owner': 'some_repo_owner'})
    assert response.status_code == 200
    assert response.get_json()["status"] == "registered"

    # Step 2: Send some messages
    for i in range(3):
        response = client.post('/log', json={'repo_name': 'some_repo_name', 'event_details': f'Test message {i}'})
        assert response.status_code == 200
        assert response.get_json()["status"] == "logged"

    # Step 3: Fetch logs
    response = client.get('/fetch-logs', query_string={'repo_name': 'some_repo_name'})
    assert response.status_code == 200
    expected_logs = ["Test message 2", "Test message 1", "Test message 0"]
    assert [entry["event_details"] for entry in response.get_json()["logs"]] == expected_logs
