from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from huey.contrib.djhuey import task


@task()
def dispatch_messages(email_messages):
    """Huey task which uses ``HUEY_EMAIL_BACKEND`` to dispatch messages."""
    try:
        backend = settings.HUEY_EMAIL_BACKEND
    except AttributeError:
        raise ImproperlyConfigured(
            "No email backend found. Please set the ``HUEY_EMAIL_BACKEND`` setting."
        )

    try:
        HueyBackend = import_string(backend)
    except ImportError:
        raise ImproperlyConfigured(
            f"Could not import email backend {backend}."
            " Please check the ``HUEY_EMAIL_BACKEND`` setting."
        )

    connection = HueyBackend()
    return connection.send_messages(email_messages)
