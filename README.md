
# Orders API — SIS 3

## Overview
A serverless and containerized Orders API deployed on AWS using CloudFormation, ECS Fargate, ECR, SQS, SNS and DynamoDB.

## Architecture
- Flask API running on ECS Fargate behind an Application Load Balancer.
- Orders sent to an SQS queue.
- Failed messages routed to a Dead Letter Queue (DLQ).
- SNS publishes OrderSubmitted domain events.
- Worker consumes SQS messages and stores orders in DynamoDB.
- DynamoDB conditional writes provide idempotent processing.
- CloudWatch stores API and worker logs.

## Infrastructure
All infrastructure is defined in `infrastructure/queues.yaml`.

Includes:
- VPC, public subnets and Application Load Balancer
- ECS Fargate API and worker services
- ECR repository with immutable image tags
- SQS queue and DLQ
- SNS topic
- DynamoDB table
- Separate IAM roles
- CloudWatch log groups with retention

## Requirements
- AWS CLI configured
- Docker Desktop
- Git
- AWS permissions for CloudFormation, ECS, ECR, IAM, SQS, SNS, DynamoDB and networking resources

## Deployment

Deploy with one command:

```bash
./scripts/deploy.sh orders-sis3-dev
```

Deploy to another stack:

```bash
./scripts/deploy.sh orders-sis3-test
```

Optional environment variables:
- `ENV` — dev or prod
- `AWS_REGION` — AWS region
- `IMAGE_TAG` — custom image tag

## API endpoints

Health check:

`GET /health`

Create order:

`POST /orders`

Example request:

```json
{
  "customer": "Test User",
  "amount": 100
}
```

List orders:

`GET /orders`

## Cleanup

Delete a stack after use:

```bash
aws cloudformation delete-stack --stack-name orders-sis3-test
```

Note: The ECR repository may need its images deleted before CloudFormation can delete it.

