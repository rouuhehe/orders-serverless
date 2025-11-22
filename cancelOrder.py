import json, boto3
from time import time
from decimal import Decimal

def to_json(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, list):
        return [to_json(x) for x in v]
    if isinstance(v, dict):
        return {k: to_json(v) for k, v in v.items()}
    return v

def lambda_handler(event, context):
    tenant_id = event["path"]["tenant_id"]
    order_id = event["path"]["order_id"]
    now = str(int(time()))

    table = boto3.resource("dynamodb").Table("dev-t_orders")

    res = table.update_item(
        Key={"tenant_id": tenant_id, "order_id": order_id},
        UpdateExpression="SET #st = :s, updatedAt = :u, isActive = :a",
        ExpressionAttributeNames={"#st": "status"},
        ExpressionAttributeValues={
            ":s": "CANCELADO",
            ":u": now,
            ":a": False
        },
        ReturnValues="ALL_NEW"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Order cancelled successfully",
            "order": to_json(res["Attributes"])
        })
    }
