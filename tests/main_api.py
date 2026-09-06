# Shared mocked GitHub responses for the real updater test.

from pathlib import Path

ROOT = Path(__file__).parents[1]


class Response:
    status_code = 200
    text = "mock"

    def __init__(self, data):
        self.data = {"data": data}

    def json(self):
        return self.data


def mocked_post(calls):
    def post(url, json, headers, timeout):
        calls.append(json)
        assert timeout == (10, 60)
        query = json["query"]
        if "createdAt" in query:
            return Response({"user": {"id": "ME", "createdAt": "2020-01-01T00:00:00Z"}})
        if "followers" in query:
            return Response({"user": {"followers": {"totalCount": 7}}})
        if "committedDate" in query:
            return history_response()
        return repositories_response()

    return post


def history_response():
    users = [("ME", 10, 2), ("OTHER", 100, 20), ("ME", 6, 1)]
    nodes = [
        {
            "node": {
                "author": {"user": {"id": who}},
                "additions": adds,
                "deletions": dels,
            }
        }
        for who, adds, dels in users
    ]
    history = {
        "edges": nodes,
        "pageInfo": {"hasNextPage": False, "endCursor": None},
        "totalCount": 3,
    }
    return Response(
        {"repository": {"defaultBranchRef": {"target": {"history": history}}}}
    )


def repositories_response():
    node = {
        "nameWithOwner": "owner/repo",
        "stargazers": {"totalCount": 5},
        "defaultBranchRef": {"target": {"history": {"totalCount": 3}}},
    }
    repos = {
        "edges": [{"node": node}],
        "totalCount": 1,
        "pageInfo": {"hasNextPage": False, "endCursor": None},
    }
    return Response({"user": {"repositories": repos}})
