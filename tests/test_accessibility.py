"""Accessibility regressions for Trovly interactive controls."""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_FILES = [ROOT / "auth.py", ROOT / "app_hosted.py", ROOT / "app.py"]
INTERACTIVE_METHODS = {"button", "link_button", "download_button", "form_submit_button"}


def _streamlit_interactions(path):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if not isinstance(node.func.value, ast.Name) or node.func.value.id != "st":
            continue
        if node.func.attr in INTERACTIVE_METHODS:
            yield node


def _argument(call, name, position=None):
    if position is not None and len(call.args) > position:
        return call.args[position]
    return next((keyword.value for keyword in call.keywords if keyword.arg == name), None)


def test_streamlit_actions_have_names_and_descriptions():
    for path in APP_FILES:
        for call in _streamlit_interactions(path):
            label = _argument(call, "label", 0)
            help_text = _argument(call, "help")

            assert label is not None, f"{path.name}:{call.lineno} is missing an accessible name"
            if isinstance(label, ast.Constant):
                assert str(label.value).strip(), f"{path.name}:{call.lineno} has an empty label"

            assert (
                help_text is not None
            ), f"{path.name}:{call.lineno} is missing help text for an accessible description"
            if isinstance(help_text, ast.Constant):
                assert str(
                    help_text.value
                ).strip(), f"{path.name}:{call.lineno} has an empty accessible description"


def test_custom_html_links_have_aria_labels():
    for path in APP_FILES:
        source = path.read_text()
        for match in re.finditer(r"<a\b[^>]*>", source, flags=re.IGNORECASE):
            tag = match.group(0)
            assert (
                "aria-label=" in tag.lower()
            ), f"{path.name} custom link is missing aria-label: {tag}"


def test_app_surfaces_keep_visible_keyboard_focus():
    for filename in ["auth.py", "app_hosted.py", "app.py"]:
        source = (ROOT / filename).read_text()
        assert ":focus-visible" in source, f"{filename} is missing keyboard focus styling"
