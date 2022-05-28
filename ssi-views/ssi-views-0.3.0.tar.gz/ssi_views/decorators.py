from .registry import registry


def ssi_view(name: str, **initkwargs):
    def decorator(view):
        registry.register(name, view, **initkwargs)
        return view

    return decorator
