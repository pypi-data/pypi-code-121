import os
import celery


def configure_app(app: celery.Celery):
    # Celery does this automatically on the client side
    # but not on the worker side.
    _module = os.environ.get("CELERY_CONFIG_MODULE")
    if _module:
        app.config_from_object(_module, force=True)
    else:
        # Warning: calling with silent=True causes sphinx doc
        # building to fail.
        try:
            import celeryconfig  # noqa F401
        except ImportError:
            pass
        else:
            app.config_from_object("celeryconfig", force=True)
