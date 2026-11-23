import json
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from flask import Flask, jsonify, request

app = Flask(__name__)

orders = []

sqs = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

QUEUE_URL = os.getenv("ORDERS_QUEUE_URL")


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/orders")
def get_orders():
    return jsonify(orders), 200


@app.post("/orders")
def create_order():
    data = request.get_json(silent=True) or {}

    if not data.get("customer") or "amount" not in data:
        return jsonify({
            "error": "customer and amount are required"
        }), 400

    if not QUEUE_URL:
        return jsonify({"error": "Queue is not configured"}), 503

    order = {
        "orderId": str(uuid.uuid4()),
        "customer": data["customer"],
        "amount": data["amount"],
        "status": "NEW"
    }

    try:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(order)
        )
    except ClientError:
        app.logger.exception("Failed to send order to SQS")
        return jsonify({"error": "Could not submit order"}), 503

    orders.append(order)

    return jsonify(order), 202
