import importlib.util
from pathlib import Path
from shutil import copyfile

from lxml import etree

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("today_svg", ROOT / "today.py")
today = importlib.util.module_from_spec(spec)
spec.loader.exec_module(today)


def test_svg_overwrite_preserves_static_content(tmp_path):
    dynamic = {
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
    for source in (ROOT / "dark_mode.svg", ROOT / "light_mode.svg"):
        target = tmp_path / source.name
        copyfile(source, target)
        before = etree.parse(target)
        expected = etree.fromstring(etree.tostring(before.getroot()))
        for element in expected.iter():
            if element.get("id") in dynamic or element.get("id", "").endswith("_dots"):
                element.text = "__DYNAMIC__"
        today.svg_overwrite(str(target), "1 year", 2, 3, 4, 5, 6, [7, 8, 9])
        after = etree.parse(target)
        for element in before.getroot().iter():
            element_id = element.get("id")
            if (
                element_id
                and element_id not in dynamic
                and not element_id.endswith("_dots")
            ):
                current = after.getroot().xpath(f".//*[@id='{element_id}']")[0]
                assert current.text == element.text
        for element in after.getroot().iter():
            if element.get("id") in dynamic or element.get("id", "").endswith("_dots"):
                element.text = "__DYNAMIC__"
        assert etree.tostring(after.getroot()) == etree.tostring(expected)
