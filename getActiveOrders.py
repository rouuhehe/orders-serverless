import json, boto3
import os

def lambda_handler(event, context):
    tenant_id = event["pathParameters"]["tenant_id"]
    table_name = os.environ["TABLE_NAME"]
    table = boto3.resource("dynamodb").Table(table_name)

    res = table.query(
        KeyConditionExpression="tenant_id = :t",
        ExpressionAttributeValues={":t": tenant_id}
    )

    active = [o for o in res["Items"] if o["status"] not in ("ENTREGADO", "CANCELADO")]

    return {
        "statusCode": 200,
        "body": json.dumps({"active_orders": active})
    }
