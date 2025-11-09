import json, boto3

def lambda_handler(event, context):
    tenant_id = event["pathParameters"]["tenant_id"]
    table = boto3.resource("dynamodb").Table("t_orders")

    res = table.query(
        KeyConditionExpression="tenant_id = :t",
        ExpressionAttributeValues={":t": tenant_id}
    )

    active = [o for o in res["Items"] if o["status"] not in ("ENTREGADO", "CANCELADO")]

    return {
        "statusCode": 200,
        "body": json.dumps({"active_orders": active})
    }
