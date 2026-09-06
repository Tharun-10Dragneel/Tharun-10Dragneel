import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_import_without_workflow_secrets():
    spec = importlib.util.spec_from_file_location("today_import", ROOT / "today.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.USER_NAME
