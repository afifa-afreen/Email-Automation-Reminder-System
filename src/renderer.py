from jinja2 import Environment, StrictUndefined, select_autoescape
from markdown import markdown

env = Environment(undefined=StrictUndefined, autoescape=select_autoescape(["html", "xml"]))

def render_email(template, context: dict) -> tuple[str, str]:
    """Render HTML and plain text from a stored template and safe context."""
    html = env.from_string(template.html_body).render(**context)
    if template.markdown_body:
        md = env.from_string(template.markdown_body).render(**context)
        plain = md
        html = markdown(md, extensions=["extra", "nl2br"])
    else:
        # Basic text fallback; HTML tags are intentionally not stripped here.
        plain = "This email is best viewed in an HTML-capable email client."
    return html, plain
