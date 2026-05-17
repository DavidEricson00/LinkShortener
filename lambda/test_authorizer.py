import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import authorizer

def event(api_key=None):
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    return {"headers": headers}

def test_valid_key_returns_authorized():
    os.environ["API_KEY"] = "my-secret-key"

    res = authorizer.handler(event(api_key="my-secret-key"), None)

    assert res["isAuthorized"] is True

def test_invalid_key_returns_unauthorized():
    os.environ["API_KEY"] = "my-secret-key"

    res = authorizer.handler(event(api_key="wrong-key"), None)

    assert res["isAuthorized"] is False


def test_missing_key_returns_unauthorized():
    os.environ["API_KEY"] = "my-secret-key"

    res = authorizer.handler(event(), None)

    assert res["isAuthorized"] is False