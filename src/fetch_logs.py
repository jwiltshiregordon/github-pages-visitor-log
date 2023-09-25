import json

import boto3
from botocore.exceptions import ClientError
from .constants import AWS_S3_BUCKET, REGISTERED_PATH, LOGS_PATH  # Adjust the import as needed


def fetch_logs(repo_name):
    s3 = boto3.client("s3")

    try:
        # Retrieve the registration object
        reg_object = s3.get_object(Bucket=AWS_S3_BUCKET, Key=f"{REGISTERED_PATH}{repo_name}")
        reg_data = json.load(reg_object['Body'])
        next_key = reg_data['next_key']
    except ClientError as e:
        return {"status": "error", "message": e.response['Error']['Message']}

    logs = []
    for i in range(100):  # Get the last 100 log messages
        cur_key = (next_key - 1 - i) % 100
        log_key = f"{LOGS_PATH}{repo_name}/{cur_key:02d}"

        try:
            log_data = s3.get_object(Bucket=AWS_S3_BUCKET, Key=log_key)['Body'].read().decode('utf-8')
            logs.append(json.loads(log_data))
        except ClientError as e:
            continue

    return {"status": "success", "logs": logs}
