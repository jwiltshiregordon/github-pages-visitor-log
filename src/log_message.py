import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError
from .constants import AWS_S3_BUCKET, LOGS_PATH, REGISTERED_PATH, NOT_REGISTERED
from .utils import get_registration_key, get_log_key, check_registration


def log_message(repo_owner, repo_name, event_details):
    s3 = boto3.client('s3')

    registered_key = get_registration_key(repo_owner, repo_name)

    try:
        registered = check_registration(s3, repo_owner, repo_name)
    except ClientError as e:
        return {
            "status": "error",
            "message": f"An S3 error occurred: {e.response['Error']['Message']}"
        }

    if not registered:
        return {
            "status": "error",
            "message": NOT_REGISTERED
        }

    # Generate the log entry
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'repo_name': repo_name,
        'event_details': event_details
    }

    try:
        reg_object = s3.get_object(Bucket=AWS_S3_BUCKET, Key=registered_key)
        registration_string = reg_object['Body'].read().decode('utf-8')
        reg_data = json.loads(registration_string)
        next_key = reg_data['next_key']
    except ClientError as e:
        return {"status": "error", "message": e.response['Error']['Message']}

    # Write log message
    log_key = get_log_key(repo_owner, repo_name, next_key)
    s3.put_object(Bucket=AWS_S3_BUCKET, Key=log_key, Body=json.dumps(log_entry))

    # Update next key in registration object
    next_key = (next_key + 1) % 100
    s3.put_object(Bucket=AWS_S3_BUCKET, Key=registered_key, Body=json.dumps({"next_key": next_key}))

    return {"status": "logged"}
