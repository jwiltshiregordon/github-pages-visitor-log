import boto3
import requests
from .constants import AWS_S3_BUCKET, REGISTERED_PATH, LOGS_PATH, CHALLENGE_FILENAME  # Adjust the import as needed


def register_repo(repo_name, repo_owner):
    s3 = boto3.client("s3")
    blob_url = f"https://github.com/{repo_owner}/{repo_name}/blob/main/{CHALLENGE_FILENAME}"
    r = requests.get(blob_url)

    registered_key = f"{REGISTERED_PATH}{repo_name}"
    log_key = f"{LOGS_PATH}{repo_name}"

    response = {}

    if r.status_code == 404:
        # Delete keys if they exist
        s3.delete_object(Bucket=AWS_S3_BUCKET, Key=registered_key)
        s3.delete_object(Bucket=AWS_S3_BUCKET, Key=log_key)
        response["status"] = "unregistered"
        response["message"] = f"File {CHALLENGE_FILENAME} not found in repository. Unregistered the repo."
    else:
        # Create or update keys
        s3.put_object(Bucket=AWS_S3_BUCKET, Key=registered_key, Body="")
        s3.put_object(Bucket=AWS_S3_BUCKET, Key=log_key, Body="")
        response["status"] = "registered"
        response["message"] = "Successfully registered the repository."

    return response
