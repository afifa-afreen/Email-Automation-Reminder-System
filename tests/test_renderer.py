from types import SimpleNamespace
from src.renderer import render_email

def test_render_personalizes_html():
    template = SimpleNamespace(
        html_body="<p>Hello {{ name }}</p>", markdown_body=None
    )
    html, plain = render_email(template, {"name": "Ada"})
    assert "Ada" in html
