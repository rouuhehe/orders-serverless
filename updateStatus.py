import json, boto3
from time import time
from decimal import Decimal
from botocore.exceptions import ClientError

def to_json(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, list):
        return [to_json(x) for x in v]
    if isinstance(v, dict):
        return {k: to_json(v) for k, v in v.items()}
    return v

def lambda_handler(event, context):
    body = event.get("body", {})
    if isinstance(body, str):
        body = json.loads(body)

    tenant_id = event["path"]["tenant_id"]
    order_id = event["path"]["order_id"]

    new_status = body.get("status")
    if new_status not in ["CREADO", "EN_PREPARACION", "EN_CAMINO", "ENTREGADO", "CANCELADO"]:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid status"})}

    table = boto3.resource("dynamodb").Table("dev-t_orders")

    try:
        res = table.update_item(
            Key={"tenant_id": tenant_id, "order_id": order_id},
            UpdateExpression="SET #st = :s, updatedAt = :u",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={
                ":s": new_status,
                ":u": str(int(time()))
            },
            ConditionExpression="attribute_exists(order_id)",
            ReturnValues="ALL_NEW"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Order status updated",
                "order": to_json(res["Attributes"])
            })
        }

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"statusCode": 404, "body": json.dumps({"error": "Order not found"})}
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
