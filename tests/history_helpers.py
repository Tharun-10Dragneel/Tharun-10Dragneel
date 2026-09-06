# Shared data builders for iterative history tests.


def response(history, branch=True):
    repo = {"defaultBranchRef": None}
    if branch:
        repo = {"defaultBranchRef": {"target": {"history": history}}}
    return type(
        "Response",
        (),
        {"status_code": 200, "json": lambda self: {"data": {"repository": repo}}},
    )()


def page(edges, cursor, more):
    return {"edges": edges, "pageInfo": {"endCursor": cursor, "hasNextPage": more}}


def edge(user, adds=1, dels=0):
    return {"node": {"author": {"user": user}, "additions": adds, "deletions": dels}}
