import json, boto3
from time import time

def lambda_handler(event, context):
    tenant_id = event["pathParameters"]["tenant_id"]
    order_id = event["pathParameters"]["order_id"]
    now = str(int(time()))

    table = boto3.resource("dynamodb").Table("t_orders")

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
            "order": res["Attributes"]
        })
    }
