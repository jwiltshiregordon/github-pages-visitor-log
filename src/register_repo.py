import json
import boto3
import requests
from .constants import AWS_S3_BUCKET, CHALLENGE_FILENAME
from .utils import get_registration_key, get_log_key, check_registration


def register_repo(repo_owner, repo_name):
    s3 = boto3.client("s3")
    # TODO allow default branches besides main and master
    blob_url = f"https://github.com/{repo_owner}/{repo_name}/blob/main/{CHALLENGE_FILENAME}"
    r = requests.get(blob_url)
    if r.status_code == 404:
        blob_url = f"https://github.com/{repo_owner}/{repo_name}/blob/master/{CHALLENGE_FILENAME}"
        r = requests.get(blob_url)

    registered_key = get_registration_key(repo_owner, repo_name)

    response = {}

    if r.status_code == 404:
        if check_registration(s3, repo_owner, repo_name):
            s3.delete_object(Bucket=AWS_S3_BUCKET, Key=registered_key)
            for index in range(100):
                log_key = get_log_key(s3, repo_owner, repo_name)
                s3.delete_object(Bucket=AWS_S3_BUCKET, Key=log_key)
        response["status"] = "unregistered"
        response["message"] = f"File {CHALLENGE_FILENAME} not found in repository. Unregistered the repo."
    elif r.status_code == 200:
        if check_registration(s3, repo_owner, repo_name):
            response["status"] = "registered"
            response["message"] = "Repository was already registered."
        else:
            s3.put_object(Bucket=AWS_S3_BUCKET, Key=registered_key, Body=json.dumps({"next_key": 0}))
            response["status"] = "registered"
            response["message"] = "Successfully registered the repository."

    return response
