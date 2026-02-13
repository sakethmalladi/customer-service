"""
MCP Server - Order Lookup Tool
- Exposes tools via the Model Context Protocol
- Agents can call these tools to look up order details
"""

import json
import os
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Order Lookup Server")

# Load order data
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_orders() -> dict:
    """Load orders from JSON file."""
    orders_path = os.path.join(DATA_DIR, "orders.json")
    with open(orders_path, "r") as f:
        return json.load(f)


@mcp.tool()
def get_order_status(order_id: str) -> str:
    """
    Look up the status and details of a customer order by order ID.

    Args:
        order_id: The order ID to look up (e.g. "1234")

    Returns:
        A formatted string with order details or an error message
    """
    data = _load_orders()
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
            # Add extra fields based on status
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


@mcp.tool()
def list_orders_by_status(status: str) -> str:
    """
    List all orders with a given status.

    Args:
        status: Order status to filter by (processing, in_transit, delivered, delayed, cancelled, refunded)

    Returns:
        A JSON string with matching orders
    """
    data = _load_orders()
    matching = [
        {"order_id": o["order_id"], "customer_name": o["customer_name"], "total": f"${o['total']:.2f}"}
        for o in data["orders"]
        if o["status"] == status
    ]
    if not matching:
        return json.dumps({"message": f"No orders found with status: {status}"})
    return json.dumps(matching, indent=2)


if __name__ == "__main__":
    mcp.run()
