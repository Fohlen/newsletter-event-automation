import html

import pytest

from newsletter_automation.message import read_mbox
from newsletter_automation.visible_text_parser import VisibleTextParser


def test_read_mbox(data_dir):
    messages = list(read_mbox(
        data_dir / "mbox",
        ["schoener-wohnen@lists.mtmedia.org"],
        "[schoener-wohnen]",
        "___________________________"
    ))
    assert len(messages) == 20


def test_visible_text(data_dir):
    with (data_dir / "visible_text.html").open() as fp:
        raw_content = fp.read()
        html_parser = VisibleTextParser()
        html_parser.feed(raw_content)
        content = html_parser.get_visible_text()
        escaped_content = html.unescape(content).strip()
        # this hardcoded number can be retrieved with document.body.innerText.length
        assert len(escaped_content) == pytest.approx(1433, rel=0.1)
