import gc
import logging
import pytest
from ewoksorange.registration import register_addon_package
from ewoksorange.bindings.qtapp import qtapp_context
from ewoksorange.bindings.qtapp import get_all_qtwidgets
from ewoksorange.canvas.handler import OrangeCanvasHandler
from .examples import ewoks_example_1_addon
from .examples import ewoks_example_2_addon
from ewoksorange import ewoks_addon
from ewoksorange.orange_version import ORANGE_VERSION


logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def register_ewoks_example_1_addon():
    register_addon_package(ewoks_example_1_addon)
    yield


@pytest.fixture(scope="session")
def register_ewoks_example_2_addon():
    register_addon_package(ewoks_example_2_addon)
    yield


@pytest.fixture(scope="session")
def register_ewoks_example_addons(
    register_ewoks_example_1_addon, register_ewoks_example_2_addon
):
    yield


def global_cleanup_orange():
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        pass
    else:
        from orangecanvas.document.suggestions import Suggestions

        Suggestions.instance = None


def global_cleanup_pytest():
    for obj in gc.get_objects():
        if isinstance(obj, logging.LogRecord):
            obj.exc_info = None  # traceback keeps frames which keep locals


def collect_garbage(app):
    app.processEvents()
    while gc.collect():
        app.processEvents()


@pytest.fixture(scope="session")
def qtapp():
    with qtapp_context() as app:
        yield app
    collect_garbage(app)
    global_cleanup_orange()
    global_cleanup_pytest()
    collect_garbage(app)
    warn_qtwidgets_alive()


@pytest.fixture(scope="session")
def raw_ewoks_orange_canvas(qtapp, register_ewoks_example_addons):
    register_addon_package(ewoks_addon)
    with OrangeCanvasHandler() as handler:
        yield handler


@pytest.fixture()
def ewoks_orange_canvas(raw_ewoks_orange_canvas):
    yield raw_ewoks_orange_canvas
    try:
        raw_ewoks_orange_canvas.scheme.ewoks_finalize()
    except AttributeError:
        pass


def warn_qtwidgets_alive():
    widgets = get_all_qtwidgets()
    if widgets:
        logger.warning(
            "%d remaining widgets after tests:\n %s",
            len(widgets),
            "\n ".join(map(str, widgets)),
        )
