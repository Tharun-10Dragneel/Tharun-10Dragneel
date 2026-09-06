# Non-retryable request error coverage.

from unittest.mock import patch

import requests
from test_retry import today


def test_invalid_url_fails_without_retry():
    with (
        patch.object(
            today.requests, "post", side_effect=requests.exceptions.InvalidURL("bad")
        ) as post,
        patch.object(today.time, "sleep") as sleep,
    ):
        try:
            today.simple_request("test", "query", {})
        except requests.exceptions.InvalidURL:
            pass
        else:
            raise AssertionError("invalid URL must fail once")
    assert post.call_count == 1
    sleep.assert_not_called()
