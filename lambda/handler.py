import json
import boto3
import os
import secrets
import time

lambda_client = None

def get_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ.get("TABLE_NAME", "links"))

def get_lambda_client():
    global lambda_client
    if lambda_client is None:
        lambda_client = boto3.client("lambda")
    return lambda_client

def create_link(event):
    try:
        table = get_table()

        raw_body = event.get("body") or ""

        if len(raw_body) > 4096:
            return {
                "statusCode": 413,
                "body": json.dumps({"error": "payload too large"})
            }

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "invalid json"})
            }

        url = body.get("url")

        if not isinstance(url, str):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "url must be string"})
            }

        url = url.strip()

        if len(url) > 2048:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "url too long"})
            }

        if not url.startswith(("http://", "https://")):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "invalid url"})
            }

        slug = secrets.token_urlsafe(4)

        expires_at = int(time.time()) + (30 * 24 * 60 * 60)

        table.put_item(
            Item={
                "id": slug,
                "url": url,
                "expires_at": expires_at
            },
            ConditionExpression="attribute_not_exists(id)"
        )

        return {
            "statusCode": 201,
            "body": json.dumps({
                "short_url": slug,
                "url": url,
                "expires_at": expires_at
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def redirect_link(slug):
    try:
        table = get_table()
        res = table.get_item(Key={"id": slug})
        item = res.get("Item")

        if not item:
            return {"statusCode": 404, "body": json.dumps({"error": "not found"})}

        try:
            get_lambda_client().invoke(
                FunctionName="link-analytics",
                InvocationType="Event",
                Payload=json.dumps({"slug": slug}).encode()
            )
        except Exception:
            pass

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
