import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("today_errors", ROOT / "today.py")
today = importlib.util.module_from_spec(spec)
spec.loader.exec_module(today)
today.ACCESS_TOKEN = "test-token"


class Response:
    def __init__(self, payload, status=200):
        self.status_code = status
        self.text = json.dumps(payload)
        self._payload = payload

    def json(self):
        return self._payload


def request_error(response, text):
    with patch.object(today.requests, "post", return_value=response):
        try:
            today.simple_request("test", "query", {})
        except RuntimeError as error:
            assert text in str(error)
        else:
            raise AssertionError("request must fail")


def test_graphql_error_is_reported():
    request_error(Response({"errors": [{"message": "bad"}]}), "GraphQL errors")


def test_http_error_is_reported():
    request_error(Response({}, 502), "HTTP 502")


def test_missing_data_is_reported():
    request_error(Response({}), "no data")


def test_timeout_is_reported():
    with patch.object(
        today.requests, "post", side_effect=today.requests.Timeout("late")
    ):
        try:
            today.simple_request("test", "query", {})
        except RuntimeError as error:
            assert "API request failed" in str(error)
        else:
            raise AssertionError("timeout must fail")


def test_missing_token_is_reported():
    token = today.ACCESS_TOKEN
    today.ACCESS_TOKEN = ""
    try:
        try:
            today.simple_request("test", "query", {})
        except RuntimeError as error:
            assert "ACCESS_TOKEN" in str(error)
        else:
            raise AssertionError("missing token must fail")
    finally:
        today.ACCESS_TOKEN = token
