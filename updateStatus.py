import json, boto3
import os
from time import time
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    body = event["body"]
    table_name = os.environ["TABLE_NAME"]
    tenant_id = event["pathParameters"]["tenant_id"]
    order_id = event["pathParameters"]["order_id"]

    new_status = body["status"]
    if new_status not in ["CREADO", "EN_PREPARACION", "EN_CAMINO", "ENTREGADO", "CANCELADO"]:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid status"})}

    table = boto3.resource("dynamodb").Table(table_name)

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
                "order": res["Attributes"]
            })
        }

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"statusCode": 404, "body": json.dumps({"error": "Order not found"})}
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
