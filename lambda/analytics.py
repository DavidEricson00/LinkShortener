import boto3
import os
import json
import time
import secrets

def get_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ.get("TABLE_NAME", "clicks"))

def handler(event, context):
    try:
        table = get_table()
        slug = event.get("slug")

        if not slug:
            return {"statusCode": 400}

        expires_at = int(time.time()) + (90 * 24 * 60 * 60) 

        table.put_item(Item={
            "id": secrets.token_urlsafe(8),
            "slug": slug,
            "timestamp": int(time.time()),
            "expires_at": expires_at
        })

        return {"statusCode": 200}
    except Exception as e:
        print(f"Analytics error: {str(e)}")
        return {"statusCode": 500}
