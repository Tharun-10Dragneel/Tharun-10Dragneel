# Durable real-entrypoint test using only mocked HTTP responses.

import os
import runpy
from unittest.mock import patch

from main_api import mocked_post
from main_harness import ROOT, assert_outputs, copy_svgs


def test_real_main_updates_stats_and_svgs(tmp_path, monkeypatch):
    calls = []
    monkeypatch.chdir(tmp_path)
    copy_svgs(tmp_path)
    env = {"ACCESS_TOKEN": "fake", "USER_NAME": "owner"}
    with patch.dict(os.environ, env), patch("requests.post", mocked_post(calls)):
        runpy.run_path(str(ROOT / "today.py"), run_name="__main__")
    assert_outputs(tmp_path)
    assert any(
        call["variables"].get("owner_affiliation") == ["OWNER"] for call in calls
    )
