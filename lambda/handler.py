import json
import boto3
import os
import secrets
import time

def get_table():
    dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    return dynamodb.Table(os.environ.get("TABLE_NAME", "links"))

def create_link(event):
    try:
        table = get_table()
        body = json.loads(event.get("body") or "{}")
        url = body.get("url")

        if not url:
            return {"statusCode": 400, "body": json.dumps({"error": "url is required"})}

        slug = secrets.token_urlsafe(4)
        expires_at = int(time.time()) + (30 * 24 * 60 * 60)
       
        table.put_item(Item={
            "id": slug,
            "url": url,
            "expires_at": expires_at
        })

        return {
            "statusCode": 201,
            "body": json.dumps({
                "short_url": slug,
                "url": url,
                "expires_at": expires_at
            })
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def redirect_link(slug):
    try:
        table = get_table()
        res = table.get_item(Key={"id": slug})
        item = res.get("Item")

        if not item:
            return {"statusCode": 404, "body": json.dumps({"error": "not found"})}

        return {
            "statusCode": 301,
            "headers": {"Location": item["url"]},
            "body": ""
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path = event["rawPath"]

    if method == "POST" and path == "/links":
        return create_link(event)

    if method == "GET" and path != "/":
        slug = path.lstrip("/")
        return redirect_link(slug)

    return {"statusCode": 404, "body": json.dumps({"error": "not found"})}
