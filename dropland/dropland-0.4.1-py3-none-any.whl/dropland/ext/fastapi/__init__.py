try:
    import starlette

    from .model import ApiModelMixin
    from .middleware import add_middleware
    from .scheduler import add_scheduler

except ImportError:
    pass
