from jinja2 import utils as jutils


def to_safe_html(s) -> str:
    return str(jutils.escape(s))