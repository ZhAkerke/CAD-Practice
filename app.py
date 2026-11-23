from flask import Flask, jsonify, request

app = Flask(__name__)
orders = []

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
        return jsonify({"error": "customer and amount are required"}), 400

    order = {
        "id": len(orders) + 1,
        "customer": data["customer"],
        "amount": data["amount"],
        "status": "NEW"
    }

    orders.append(order)
    return jsonify(order), 201
