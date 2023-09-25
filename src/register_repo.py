import boto3

def register_repo(repo_name):
    s3 = boto3.client("s3")
    
    # Create two documents on S3 for registered repo and logs
    s3.put_object(Bucket="my_test_bucket", Key=f"registered/{repo_name}", Body="")
    s3.put_object(Bucket="my_test_bucket", Key=f"logs/{repo_name}", Body="")
