import boto3
import requests


def register_repo(repo_name, repo_owner):
    # Check for .github-pages-visitor-log in GitHub repo
    blob_url = f"https://github.com/{repo_owner}/{repo_name}/blob/main/.github-pages-visitor-log"

    r = requests.get(blob_url)

    if r.status_code == 404:
        return "File .github-pages-visitor-log not found in repository"

    s3 = boto3.client("s3")

    # Create two documents on S3 for registered repo and logs
    s3.put_object(Bucket="my_test_bucket", Key=f"registered/{repo_name}", Body="")
    s3.put_object(Bucket="my_test_bucket", Key=f"logs/{repo_name}", Body="")

    return "Successfully registered"
