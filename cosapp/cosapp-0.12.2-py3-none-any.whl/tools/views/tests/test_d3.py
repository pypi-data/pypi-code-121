"""Dummy call on D3 views"""
import pytest

from cosapp.tests.library.systems import FanComplex
from cosapp.tools.views.d3js import  D3JsRenderer
from cosapp.utils.testing import no_exception, assert_keys

pytest.importorskip("jinja2")


@pytest.fixture(scope="function")
def fan():
    return FanComplex("fan")


@pytest.fixture(scope="function")
def renderer(fan):
    return D3JsRenderer(fan)


def test_D3JsRenderer_get_level(fan):
    level = D3JsRenderer.get_level(fan)
    assert level == 3


def test_D3JsRenderer_html_tags(renderer):
    tags = renderer.html_tags()
    assert_keys(
        tags,
        "html_begin_tags",
        "html_end_tags",
    )


def test_D3JsRenderer_html_resources(renderer):
    resources = renderer.html_resources()
    assert_keys(resources, "d3_js", "draw_js", "d3_styles")


def test_D3JsRenderer_html_template(renderer):
    with no_exception():
        template = renderer.html_template()


def test_D3JsRenderer_get_globals(renderer):

    common = renderer.get_globals()
    assert_keys(
        common,
        "template",
        "html_begin_tags",
        "html_end_tags",
        "d3_js",
        "draw_js",
        "d3_styles",
    )


def test_D3JsRenderer_html_content(renderer):
    with no_exception():
        renderer.html_content()
