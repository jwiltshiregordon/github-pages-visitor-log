import boto3
import requests
from .constants import AWS_S3_BUCKET, REGISTERED_PATH, LOGS_PATH, CHALLENGE_FILENAME


def register_repo(repo_name, repo_owner):
    blob_url = f"https://github.com/{repo_owner}/{repo_name}/blob/main/{CHALLENGE_FILENAME}"
    r = requests.get(blob_url)
    if r.status_code == 404:
        return f"File {CHALLENGE_FILENAME} not found in repository"

    s3 = boto3.client("s3")

    s3.put_object(Bucket=AWS_S3_BUCKET, Key=f"{REGISTERED_PATH}{repo_name}", Body="")
    s3.put_object(Bucket=AWS_S3_BUCKET, Key=f"{LOGS_PATH}{repo_name}", Body="")

    return "Successfully registered"
