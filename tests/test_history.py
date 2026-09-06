# Iterative filtered repository history traversal coverage.

import importlib.util
from pathlib import Path
from unittest.mock import patch

from history_helpers import edge, page, response

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("today_history", ROOT / "today.py")
today = importlib.util.module_from_spec(spec)
spec.loader.exec_module(today)
today.OWNER_ID = {"id": "ME"}
today.ACCESS_TOKEN = "test-token"


def test_history_iterates_more_than_one_hundred_filtered_entries():
    pages = [
        response(page([edge({"id": "ME"})], str(index + 1), True))
        for index in range(100)
    ]
    pages.append(
        response(
            page(
                [
                    edge({"id": "ME"}, 4, 1),
                    edge({"id": "OTHER"}, 20, 5),
                    edge(None, 8, 2),
                ],
                None,
                False,
            )
        )
    )
    with patch.object(today, "simple_request", side_effect=pages) as request:
        assert today.recursive_loc("owner", "repo", [], []) == (104, 1, 101)
    assert request.call_count == 101
    assert request.call_args_list[0].args[2]["authorId"] == "ME"
    assert "author: {id: $authorId}" in request.call_args_list[0].args[1]


def test_empty_repository_returns_zero_history():
    with patch.object(today, "simple_request", return_value=response({}, False)):
        assert today.recursive_loc("owner", "empty", [], []) == (0, 0, 0)


def test_empty_filtered_history_returns_zero():
    with patch.object(
        today, "simple_request", return_value=response(page([], None, False))
    ):
        assert today.recursive_loc("owner", "repo", [], []) == (0, 0, 0)


def test_history_cursor_must_advance():
    with patch.object(
        today,
        "simple_request",
        return_value=response(page([edge({"id": "ME"})], None, True)),
    ):
        try:
            today.recursive_loc("owner", "repo", [], [])
        except RuntimeError as error:
            assert "did not advance" in str(error)
        else:
            raise AssertionError("stalled history pagination must fail")
