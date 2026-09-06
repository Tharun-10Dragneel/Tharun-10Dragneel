import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("today_api", ROOT / "today.py")
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


def test_stars_are_paginated():
    pages = [
        {
            "data": {
                "user": {
                    "repositories": {
                        "edges": [{"node": {"stargazers": {"totalCount": 2}}}],
                        "totalCount": 2,
                        "pageInfo": {"hasNextPage": True, "endCursor": "next"},
                    }
                }
            }
        },
        {
            "data": {
                "user": {
                    "repositories": {
                        "edges": [{"node": {"stargazers": {"totalCount": 3}}}],
                        "totalCount": 2,
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        },
    ]
    with patch.object(today.requests, "post", side_effect=[Response(p) for p in pages]):
        assert today.graph_repos_stars("stars", ["OWNER"]) == 5


def test_star_pagination_rejects_stalled_cursor():
    page = {
        "data": {
            "user": {
                "repositories": {
                    "edges": [],
                    "totalCount": 1,
                    "pageInfo": {"hasNextPage": True, "endCursor": None},
                }
            }
        }
    }
    with patch.object(today.requests, "post", return_value=Response(page)):
        try:
            today.graph_repos_stars("stars", ["OWNER"])
        except RuntimeError as error:
            assert "did not advance" in str(error)
        else:
            raise AssertionError("stalled pagination must fail")
