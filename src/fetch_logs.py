import json
from concurrent.futures import ThreadPoolExecutor

import boto3
from botocore.exceptions import ClientError
from .constants import AWS_S3_BUCKET
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
    log_keys = [get_log_key(repo_owner, repo_name, (next_key - 1 - i) % 100) for i in range(100)]

    def fetch_log(log_key):
        try:
            log_data = s3.get_object(Bucket=AWS_S3_BUCKET, Key=log_key)['Body'].read().decode('utf-8')
            return json.loads(log_data)
        except ClientError as e:
            return None

    with ThreadPoolExecutor() as executor:
        for log in executor.map(fetch_log, log_keys):
            if log is not None:
                logs.append(log)

    print("I did it!")
    print(logs)
    return logs
