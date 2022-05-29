from django.core.mail.backends.base import BaseEmailBackend

from hueymail.tasks import dispatch_messages


class EmailBackend(BaseEmailBackend):
    """Email backend which dispatches messages via Huey."""

    def send_messages(self, email_messages):
        """Send messages via the Huey backend.

        Returns
        -------
        The number of email messages dispatched to Huey. This is NOT the same as
        the number of emails successfully delivered.
        """
        if not email_messages:
            return 0

        dispatch_messages(email_messages)
        return len(email_messages)
