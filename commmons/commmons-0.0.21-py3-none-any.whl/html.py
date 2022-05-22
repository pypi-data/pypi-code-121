import requests
from lxml import html
from lxml.html import HtmlElement

__all__ = [
    "html_from_url",
    "html_to_string"
]


def html_from_url(url, **kwargs) -> HtmlElement:
    r = requests.get(url, **kwargs)
    r.raise_for_status()
    return html.fromstring(r.text)


def html_to_string(e: HtmlElement):
    return html.tostring(e, encoding="utf-8").decode("utf-8")
