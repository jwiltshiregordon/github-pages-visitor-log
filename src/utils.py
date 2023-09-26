from src.constants import REGISTERED_PATH, LOGS_PATH, AWS_S3_BUCKET, NOT_REGISTERED
from botocore.exceptions import ClientError


def get_registration_key(repo_owner, repo_name):
    return f"{REGISTERED_PATH}{repo_owner}/{repo_name}"


def get_log_key(repo_owner, repo_name, index):
    return f"{LOGS_PATH}{repo_owner}/{repo_name}/{index:02d}"


def check_registration(s3, repo_owner, repo_name):
    registered_key = get_registration_key(repo_owner, repo_name)
    try:
        s3.head_object(Bucket=AWS_S3_BUCKET, Key=registered_key)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise e
    return True
