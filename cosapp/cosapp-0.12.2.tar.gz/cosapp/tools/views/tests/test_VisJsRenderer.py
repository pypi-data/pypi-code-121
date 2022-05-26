import pytest

from cosapp.tests.library.systems import FanComplex
from cosapp.tools.views.visjs import VisJsRenderer
from cosapp.utils.testing import no_exception, assert_keys


pytest.importorskip("jinja2")


@pytest.fixture(scope="function")
def fan():
    return FanComplex("fan")


@pytest.fixture(scope="function")
def renderer(fan):
    return VisJsRenderer(fan)


def test_VisJsRenderer_html_tags(renderer):
    tags = renderer.html_tags()
    assert_keys(tags, "html_begin_tags", "html_end_tags")


def test_VisJsRenderer_html_resources(renderer):
    resources = renderer.html_resources()
    assert_keys(resources, "visJS", "visCSS")


def test_VisJsRenderer_html_template(renderer):
    with no_exception():
        template = renderer.html_template()


def test_VisJsRenderer_get_globals(renderer):

    common = renderer.get_globals()
    assert_keys(
        common, "template", "html_begin_tags", "html_end_tags", "visJS", "visCSS"
    )


def test_VisJsRenderer_html_content(renderer):
    with no_exception():
        renderer.html_content()
