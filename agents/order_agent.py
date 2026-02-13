"""
Order Agent
- Receives order-related queries
- Calls the MCP order lookup tool to fetch order details
- Returns order information to the orchestrator
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def get_order_status(order_id: str) -> str:
    """
    Look up order details by order ID.

    Args:
        order_id: The order ID (e.g. "1234")

    Returns:
        JSON string with order details
    """
    orders_path = os.path.join(DATA_DIR, "orders.json")
    with open(orders_path, "r") as f:
        data = json.load(f)

    for order in data["orders"]:
        if order["order_id"] == order_id:
            result = {
                "order_id": order["order_id"],
                "customer_name": order["customer_name"],
                "status": order["status"],
                "items": [item["name"] for item in order["items"]],
                "total": f"${order['total']:.2f}",
                "shipping_method": order["shipping_method"],
                "order_date": order["order_date"],
                "estimated_delivery": order["estimated_delivery"],
                "tracking_number": order["tracking_number"],
            }
            if order["status"] == "delivered":
                result["actual_delivery"] = order.get("actual_delivery")
            elif order["status"] == "delayed":
                result["delay_reason"] = order.get("delay_reason")
            elif order["status"] == "cancelled":
                result["cancellation_reason"] = order.get("cancellation_reason")
            elif order["status"] == "refunded":
                result["refund_reason"] = order.get("refund_reason")
                result["refund_amount"] = f"${order.get('refund_amount', 0):.2f}"
                result["refund_date"] = order.get("refund_date")

            return json.dumps(result, indent=2)

    return json.dumps({"error": f"Order #{order_id} not found"})
