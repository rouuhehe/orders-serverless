import json, boto3, uuid
from time import time
from decimal import Decimal, InvalidOperation

from decimal import Decimal

def safe_decimal(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return Decimal(str(value))

    if isinstance(value, str):
        return value  # no tocar strings

    if isinstance(value, list):
        return [safe_decimal(v) for v in value]

    if isinstance(value, dict):
        return {k: safe_decimal(v) for k, v in value.items()}

    return value


def lambda_handler(event, context):
    print("EVENT BODY RAW:", event.get("body"))

    body_raw = event.get("body", "{}")
    body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw

    path_params = event.get("path", {})
    tenant_id = path_params.get("tenant_id")

    order_id = str(uuid.uuid4())
    now = str(int(time()))

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("dev-t_orders")

    order_data = {
        "tenant_id": tenant_id,
        "order_id": order_id,
        "customer_id": body["customer_id"],
        "items": body["items"],
        "total": body["total"],

        "status": "CREADO",
        "delivery_address": body.get("delivery_address"),
        "estimated_time": body.get("estimated_time"),
        "staff_id": body.get("staff_id"),

        "isActive": True,
        "createdAt": now,
        "updatedAt": now
    }

    order_data = safe_decimal(order_data)

    table.put_item(Item=order_data)

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Order created", "order_id": order_id})
    }
