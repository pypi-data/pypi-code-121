from tuxmake.build import BuildInfo


def test_status():
    info = BuildInfo("PASS")
    assert info.status == "PASS"


def test_failed():
    assert BuildInfo("FAIL").failed
    assert not BuildInfo("PASS").failed
    assert not BuildInfo("SKIP").failed


def test_passed():
    assert BuildInfo("PASS").passed
    assert not BuildInfo("FAIL").passed
    assert not BuildInfo("SKIP").passed


def test_skipped():
    assert BuildInfo("SKIP").skipped
    assert not BuildInfo("FAIL").skipped
    assert not BuildInfo("PASS").skipped


def test_duration():
    info = BuildInfo("PASS", 1)
    assert info.duration == 1
