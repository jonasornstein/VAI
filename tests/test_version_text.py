from pathlib import Path

from vai import __version__
from vai.server import VERSION_PLACEHOLDER, render_index_html

UI = Path(__file__).resolve().parents[1] / "outbox/mockups/v85-proposal-ux-mockup-atg.html"


def test_ui_has_no_hardcoded_version():
    html = UI.read_text(encoding="utf-8")
    assert VERSION_PLACEHOLDER in html
    assert __version__ not in html.replace(VERSION_PLACEHOLDER, "")


def test_render_index_uses_package_version():
    out = render_index_html(UI.read_text(encoding="utf-8"))
    assert VERSION_PLACEHOLDER not in out
    assert out.count("v" + __version__) >= 5
