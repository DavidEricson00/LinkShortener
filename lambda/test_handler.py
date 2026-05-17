import json
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import handler

def event(method, path, body=None):
    return {
        "requestContext": {"http": {"method": method}},
        "rawPath": path,
        "body": json.dumps(body) if body else None
    }

@patch("handler.get_table")
def test_create_link_returns_201(mock_get_table):
    mock_table = MagicMock()
    mock_get_table.return_value = mock_table

    res = handler.create_link(event("POST", "/links", {"url": "https://github.com"}))

    assert res["statusCode"] == 201
    data = json.loads(res["body"])
    assert "short_url" in data
    assert "expires_at" in data
    assert data["url"] == "https://github.com"

@patch("handler.get_table")
def test_create_link_without_url_returns_400(mock_get_table):
    res = handler.create_link(event("POST", "/links", {}))

    assert res["statusCode"] == 400

@patch("handler.get_table")
def test_redirect_existing_link(mock_get_table):
    mock_table = MagicMock()
    mock_get_table.return_value = mock_table
    mock_table.get_item.return_value = {
        "Item": {"id": "xK3p9", "url": "https://github.com"}
    }

    res = handler.redirect_link("xK3p9")

    assert res["statusCode"] == 301
    assert res["headers"]["Location"] == "https://github.com"

@patch("handler.get_table")
def test_redirect_nonexistent_link(mock_get_table):
    mock_table = MagicMock()
    mock_get_table.return_value = mock_table
    mock_table.get_item.return_value = {}

    res = handler.redirect_link("aaaaa")

    assert res["statusCode"] == 404

@patch("handler.get_table")
def test_route_not_found(mock_get_table):
    res = handler.handler(event("GET", "/"), None)

    assert res["statusCode"] == 404
