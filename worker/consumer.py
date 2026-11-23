import json
import os

import boto3
from botocore.exceptions import ClientError

REGION = os.getenv("AWS_REGION", "us-east-1")

sqs = boto3.client("sqs", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)

QUEUE_URL = os.environ["ORDERS_QUEUE_URL"]
TABLE_NAME = os.environ["ORDERS_TABLE"]

table = dynamodb.Table(TABLE_NAME)


def process_message(message):
    order = json.loads(message["Body"])
    order_id = order["orderId"]

    try:
        table.put_item(
            Item=order,
            ConditionExpression="attribute_not_exists(orderId)"
        )
        print(f"Processed order: {order_id}")

    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print(f"Duplicate order ignored: {order_id}")
        else:
            raise


def main():
    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )

        for message in response.get("Messages", []):
            try:
                process_message(message)

                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=message["ReceiptHandle"]
                )

            except Exception as error:
                print(f"Processing failed: {error}")


if __name__ == "__main__":
    main()
