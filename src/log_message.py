import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError
from .constants import AWS_S3_BUCKET, LOGS_PATH, REGISTERED_PATH, NOT_REGISTERED


def log_message(repo_name, event_details):
    s3 = boto3.client('s3')

    registered_key = f"{REGISTERED_PATH}{repo_name}"

    # Check if repository is registered
    try:
        s3.head_object(Bucket=AWS_S3_BUCKET, Key=registered_key)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return {
                "status": "error",
                "message": NOT_REGISTERED
            }
        else:
            return {
                "status": "error",
                "message": f"An S3 error occurred: {e.response['Error']['Message']}"
            }

    # Generate the log entry
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'repo_name': repo_name,
        'event_details': event_details
    }

    try:
        reg_object = s3.get_object(Bucket=AWS_S3_BUCKET, Key=f"{REGISTERED_PATH}{repo_name}")
        registration_string = reg_object['Body'].read().decode('utf-8')
        reg_data = json.loads(registration_string)
        next_key = reg_data['next_key']
    except ClientError as e:
        return {"status": "error", "message": e.response['Error']['Message']}

    # Write log message
    log_key = f"{LOGS_PATH}{repo_name}/{next_key:02d}"
    s3.put_object(Bucket=AWS_S3_BUCKET, Key=log_key, Body=json.dumps(log_entry))

    # Update next key in registration object
    next_key = (next_key + 1) % 100
    s3.put_object(Bucket=AWS_S3_BUCKET, Key=f"{REGISTERED_PATH}{repo_name}", Body=json.dumps({"next_key": next_key}))

    return {"status": "logged"}
