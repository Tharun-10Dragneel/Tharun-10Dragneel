import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("today_cache", ROOT / "today.py")
today = importlib.util.module_from_spec(spec)
spec.loader.exec_module(today)


def test_commit_counter_uses_authored_cache_column(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cache = tmp_path / "cache"
    cache.mkdir()
    name = hashlib.sha256(today.USER_NAME.encode()).hexdigest() + ".txt"
    (cache / name).write_text("repo-a 8 4 10 2\nrepo-b 9 7 3 1\n")
    assert today.commit_counter(0) == 11


def test_cache_reindexes_repository_order(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cache = tmp_path / "cache"
    cache.mkdir()
    name = hashlib.sha256(today.USER_NAME.encode()).hexdigest() + ".txt"
    first = hashlib.sha256(b"owner/first").hexdigest()
    second = hashlib.sha256(b"owner/second").hexdigest()
    (cache / name).write_text(f"{second} 0 2 5 1\n{first} 0 3 7 2\n")
    edges = [
        {"node": {"nameWithOwner": "owner/first", "defaultBranchRef": None}},
        {"node": {"nameWithOwner": "owner/second", "defaultBranchRef": None}},
    ]
    assert today.cache_builder(edges, 0, False)[:3] == [12, 3, 9]


def test_empty_repository_has_zero_history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cache = tmp_path / "cache"
    cache.mkdir()
    name = hashlib.sha256(today.USER_NAME.encode()).hexdigest() + ".txt"
    repo = {"node": {"nameWithOwner": "owner/empty", "defaultBranchRef": None}}
    (cache / name).write_text(hashlib.sha256(b"owner/empty").hexdigest() + " 0 0 0 0\n")
    assert today.cache_builder([repo], 0, False)[:3] == [0, 0, 0]
