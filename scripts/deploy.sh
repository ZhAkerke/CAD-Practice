#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="${1:-orders-sis3-dev}"
ENV="${ENV:-dev}"
AWS_REGION="${AWS_REGION:-us-east-1}"
TEMPLATE="infrastructure/queues.yaml"

GIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${IMAGE_TAG:-${GIT_SHA}-$(date +%Y%m%d%H%M%S)}"

echo "Deploying stack: $STACK_NAME"
echo "Region: $AWS_REGION"
echo "Image tag: $IMAGE_TAG"

# Create infrastructure without starting ECS tasks
aws cloudformation deploy \
  --template-file "$TEMPLATE" \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Env="$ENV" \
    ImageTag="$IMAGE_TAG" \
    DesiredCount=0

# Get ECR repository URI
REPO_URI=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='ECRRepositoryUri'].OutputValue" \
  --output text)

if [[ -z "$REPO_URI" || "$REPO_URI" == "None" ]]; then
  echo "ERROR: ECRRepositoryUri output not found."
  exit 1
fi

# Authenticate Docker with ECR
REGISTRY="${REPO_URI%%/*}"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

# Build and push image
docker buildx build \
  --platform linux/amd64 \
  --tag "$REPO_URI:$IMAGE_TAG" \
  --push .

# Start ECS services
aws cloudformation deploy \
  --template-file "$TEMPLATE" \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Env="$ENV" \
    ImageTag="$IMAGE_TAG" \
    DesiredCount=1

echo "Deployment completed!"
echo "Stack: $STACK_NAME"
echo "Image: $REPO_URI:$IMAGE_TAG"
