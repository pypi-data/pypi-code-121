from pathlib import Path
from packaging import version

from service import fn

assert fn.is_testing()


def test_smoke():
    """Smoke tests."""
    assert 'service' in fn.project_dir().as_posix()


def test_get_version():
    """Check read project version."""
    read_version = fn.get_version()
    version_min = version.parse('0.0.0')
    version_max = version.parse('999.0.0')  # need smoke after xD
    assert version_min < version.parse(read_version) < version_max


def test_poetry_config_path():
    """Check valid poetry config."""
    assert Path(fn.poetry_config_path).exists()


def test_poetry_config():
    """Check valid poetry config."""
    assert fn.poetry_config['tool']['poetry']['name'] == 'pbt-service'
    assert fn.poetry_config['tool']['poetry']['version'] == fn.get_version()
