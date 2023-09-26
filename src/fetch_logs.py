import json

import boto3
from botocore.exceptions import ClientError
from .constants import AWS_S3_BUCKET, REGISTERED_PATH, LOGS_PATH  # Adjust the import as needed
from .utils import get_registration_key, get_log_key


def fetch_logs(repo_owner, repo_name):
    s3 = boto3.client("s3")

    try:
        reg_key = get_registration_key(repo_owner, repo_name)
        reg_object = s3.get_object(Bucket=AWS_S3_BUCKET, Key=reg_key)
        reg_data = json.load(reg_object['Body'])
        next_key = reg_data['next_key']
    except ClientError as e:
        return {"status": "error", "message": e.response['Error']['Message']}

    logs = []
    for index in range(100):  # Get the last 100 log messages
        cur_key = (next_key - 1 - index) % 100
        log_key = get_log_key(repo_owner, repo_name, cur_key)

        try:
            log_data = s3.get_object(Bucket=AWS_S3_BUCKET, Key=log_key)['Body'].read().decode('utf-8')
            logs.append(json.loads(log_data))
        except ClientError as e:
            continue

    return {"status": "success", "logs": logs}
