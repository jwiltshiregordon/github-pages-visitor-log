# GitHub Visitor Count and Logging API

## Overview

This API allows GitHub Pages owners to log visitor counts and messages. If you want to log messages on your GitHub Pages repo, you simply need to add a `.github_visitor_counts` file in the root of your repo and register it with our API. This service is built on AWS Lambda and SQS and is designed to be simple and scalable.

## API Endpoints

### Register Repository

- **Endpoint**: `/register`
- **Method**: `POST`
- **Payload**: `{ "repoName": "your_repo_name" }`
- **Response**: 200 OK, 400 Bad Request
- **Description**: Registers a repository for tracking. Creates two S3 files: `registered/reponame` and `logs/reponame`.

### Log Message

- **Endpoint**: `/log`
- **Method**: `POST`
- **Payload**: `{ "repoName": "your_repo_name", "message": "your_message" }`
- **Response**: 200 OK, 400 Bad Request
- **Description**: Logs a message to the registered repository. Only the first 1000 characters are retained.

### Get Logs

- **Endpoint**: `/logs`
- **Method**: `GET`
- **Query Params**: `repoName=your_repo_name`
- **Response**: 200 OK, 400 Bad Request, logs as JSON
- **Description**: Retrieves logs for a registered repository.

## Architecture

### Overview

1. **AWS Lambda**: A single Lambda function is responsible for all API logic including registration, logging, and fetching logs.
2. **AWS SQS**: An SQS queue temporarily holds log messages before they are processed by the Lambda function.
3. **AWS S3**: Stores registered repositories and logs.

### Data Flow

1. A user registers their GitHub repo through the `/register` API endpoint. The Lambda function writes to S3 to indicate that this repo is registered.
2. A script on the user's GitHub Pages sends log messages to the `/log` API endpoint.
3. The Lambda function puts these log messages into an SQS queue.
4. The same Lambda function is triggered by the SQS queue to process messages. It appends each message to the appropriate log file in S3.
5. Users can fetch their logs using the `/logs` API endpoint. The Lambda function reads the appropriate log file from S3 and returns it.

### Additional Features

1. **Rate Limiting**: Stochastic dropping of messages is implemented to manage throughput.
2. **Log Rotation**: Logs are limited to 100 lines, each with a maximum of 1000 characters.
3. **Free Tier**: The system is designed to stay within AWS Free Tier limits, offering 1 million free SQS requests per month and 1 million free Lambda invocations per month.

### Future Enhancements

1. **DDoS Protection**: Future versions may include AWS WAF for DDoS protection and rate limiting.
2. **Cost Management**: AWS Budgets may be used for monitoring costs as popularity increases.
