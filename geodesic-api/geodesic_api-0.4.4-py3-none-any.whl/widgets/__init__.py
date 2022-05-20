try:
    from jinja2 import Environment, PackageLoader, select_autoescape
    JINJA = True
except ImportError:
    JINJA = False

__all__ = ["get_template_env", "jinja_available"]


_template_environment = None


def get_template_env():
    global _template_environment
    if _template_environment is not None:
        return _template_environment
    else:
        _template_environment = Environment(
            loader=PackageLoader("geodesic.widgets", "templates"),
            autoescape=select_autoescape()
        )
        return _template_environment


def jinja_available() -> bool:
    if JINJA:
        return True
    else:
        return False
