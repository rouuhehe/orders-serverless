import json
import boto3
from decimal import Decimal

def to_json(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [to_json(v) for v in value]
    if isinstance(value, dict):
        return {k: to_json(v) for k, v in value.items()}
    return value

def lambda_handler(event, context):
    tenant_id = event["path"]["tenant_id"]
    table = boto3.resource("dynamodb").Table("dev-t_orders")

    res = table.query(
        KeyConditionExpression="tenant_id = :t",
        ExpressionAttributeValues={":t": tenant_id}
    )

    active = [o for o in res["Items"] if o["status"] not in ("ENTREGADO", "CANCELADO")]
    active = to_json(active)

    return {
        "statusCode": 200,
        "body": json.dumps({"active_orders": active})
    }
