from ..client import celery
from ..client import process
from .utils import get_result


def test_convert(ewoks_worker, tmpdir):
    assert_convert(celery, tmpdir)


def test_convert_local(local_ewoks_worker, tmpdir):
    assert_convert(process, tmpdir)


def assert_convert(mod, tmpdir):
    filename = tmpdir / "test.json"
    args = {"graph": {"idd": "testgraph", "version": "1.0"}}, str(filename)
    kwargs = {"save_options": {"indent": 2}}
    future = mod.convert_workflow(args=args, kwargs=kwargs)
    results = get_result(future, timeout=3)
    assert results is None
    assert filename.exists()
