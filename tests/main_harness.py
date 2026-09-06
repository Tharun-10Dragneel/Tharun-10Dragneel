# Static SVG assertions for the real updater entrypoint test.

import shutil
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).parents[1]
DYNAMIC = {
    "age_data",
    "commit_data",
    "star_data",
    "repo_data",
    "contrib_data",
    "follower_data",
    "loc_data",
    "loc_add",
    "loc_del",
}
EXPECTED = {
    "commit_data": "2",
    "star_data": "5",
    "repo_data": "1",
    "contrib_data": "1",
    "follower_data": "7",
    "loc_add": "16",
    "loc_del": "3",
    "loc_data": "13",
}


def copy_svgs(folder):
    (folder / "cache").mkdir()
    for name in ("dark_mode.svg", "light_mode.svg"):
        shutil.copyfile(ROOT / name, folder / name)


def assert_outputs(folder):
    for name in ("dark_mode.svg", "light_mode.svg"):
        actual = etree.parse(folder / name)
        original = etree.parse(ROOT / name)
        for key, value in EXPECTED.items():
            assert actual.find(f'.//*[@id="{key}"]').text == value
        normalize(original.getroot())
        normalize(actual.getroot())
        assert etree.tostring(original.getroot()) == etree.tostring(actual.getroot())


def normalize(root):
    for element in root.iter():
        if element.get("id") in DYNAMIC or element.get("id", "").endswith("_dots"):
            element.text = "__DYNAMIC__"
