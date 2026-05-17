import os

def handler(event, context):
    token = event.get("headers", {}).get("x-api-key", "")
    expected = os.environ.get("API_KEY", "")

    if token and token == expected:
        return {"isAuthorized": True}

    return {"isAuthorized": False}
