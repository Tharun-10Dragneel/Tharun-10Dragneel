# Retry behavior for transient and non-transient GitHub responses.

import importlib.util
from unittest.mock import patch

import requests

ROOT = __import__("pathlib").Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("today_retry", ROOT / "today.py")
today = importlib.util.module_from_spec(spec)
spec.loader.exec_module(today)
today.ACCESS_TOKEN = "test-token"


class Response:
    def __init__(self, status, payload=None):
        self.status_code = status
        self.text = "response"
        self.payload = payload or {"data": {}}

    def json(self):
        return self.payload


def test_transient_http_error_retries_then_succeeds():
    responses = [Response(503), Response(502), Response(200)]
    with (
        patch.object(today.requests, "post", side_effect=responses) as post,
        patch.object(today.time, "sleep") as sleep,
    ):
        assert today.simple_request("test", "query", {}) is responses[-1]
    assert post.call_count == 3
    assert sleep.call_count == 2


def test_transient_network_error_retries_then_succeeds():
    responses = [requests.ConnectionError("reset"), Response(200)]
    with (
        patch.object(today.requests, "post", side_effect=responses),
        patch.object(today.time, "sleep"),
    ):
        assert today.simple_request("test", "query", {}).status_code == 200


def test_transient_errors_fail_after_bounded_retries():
    with (
        patch.object(today.requests, "post", return_value=Response(504)) as post,
        patch.object(today.time, "sleep"),
    ):
        try:
            today.simple_request("test", "query", {})
        except RuntimeError as error:
            assert "HTTP 504" in str(error)
        else:
            raise AssertionError("retry exhaustion must fail")
    assert post.call_count == today.MAX_RETRIES + 1


def test_auth_error_does_not_retry():
    with (
        patch.object(today.requests, "post", return_value=Response(401)) as post,
        patch.object(today.time, "sleep") as sleep,
    ):
        try:
            today.simple_request("test", "query", {})
        except RuntimeError as error:
            assert "HTTP 401" in str(error)
        else:
            raise AssertionError("auth errors must fail")
    assert post.call_count == 1
    sleep.assert_not_called()
