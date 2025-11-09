import json, boto3, uuid
from time import time

def lambda_handler(event, context):
    body = event["body"]
    tenant_id = event["pathParameters"]["tenant_id"]

    order_id = str(uuid.uuid4())
    now = str(int(time()))

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("t_orders")

    order_data = {
        "tenant_id": tenant_id,
        "order_id": order_id,
        "customer_id": body["customer_id"],

        "items": body["items"],  # lista de objetos [{item_id, name, qty, price}]
        "total": float(body["total"]),
        "status": "CREADO",
        "delivery_address": body.get("delivery_address", {
            "street": body.get("street"),
            "city": body.get("city"),
            "district": body.get("district"),
            "reference": body.get("reference"),
            "lat": body.get("lat"),
            "lng": body.get("lng")
        }),
        "estimated_time": body.get("estimated_time"),  

        "staff_id": body.get("staff_id"),
        "isActive": True,
        "createdAt": now,
        "updatedAt": now
    }

    table.put_item(Item=order_data)

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Order created", "order_id": order_id})
    }
