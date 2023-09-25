import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError
from .constants import AWS_S3_BUCKET, LOGS_PATH, REGISTERED_PATH  # Adjust the import as needed


def log_message(repo_name, event_details):
    s3 = boto3.client('s3')

    registered_key = f"{REGISTERED_PATH}{repo_name}"

    # Check if repository is registered
    try:
        s3.head_object(Bucket=AWS_S3_BUCKET, Key=registered_key)
    except ClientError as e:
        # Object does not exist or access denied - assume repo is not registered
        if e.response['Error']['Code'] == '404':
            return {
                "status": "error",
                "message": "Repository not registered, can't log event."
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

    log_key = f"{LOGS_PATH}{repo_name}/{datetime.utcnow().isoformat()}.json"

    # Serialize to a JSON string
    log_entry_str = json.dumps(log_entry)

    # Store in S3 bucket
    s3.put_object(Bucket=AWS_S3_BUCKET, Key=log_key, Body=log_entry_str)

    return {
        "status": "success",
        "message": "Successfully logged event."
    }
