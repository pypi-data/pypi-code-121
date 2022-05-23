from enum import Enum

_OrangeVersion = Enum("OrangeVersion", "latest_orange oasys_fork latest_orange_base")

try:
    import oasys.widgets  # noqa F401

    ORANGE_VERSION = _OrangeVersion.oasys_fork
except ImportError:
    try:
        import Orange  # noqa F401
    except ImportError:
        ORANGE_VERSION = _OrangeVersion.latest_orange_base
    else:
        ORANGE_VERSION = _OrangeVersion.latest_orange
