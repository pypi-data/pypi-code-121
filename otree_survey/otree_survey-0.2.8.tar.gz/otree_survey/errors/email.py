from copy import copy
from django.conf import settings
from django.core import serializers
from django.views.debug import ExceptionReporter
from django.utils.log import AdminEmailHandler
from .utils import (
    get_participant_from_path_or_none,
    get_participant_last_player_or_none,
    get_error_code,
)


class CustomAdminEmailHandler(AdminEmailHandler):
    def emit(self, record):
        if settings.DEBUG or not settings.EMAIL_HOST:
            return

        # Participant objects
        request = None
        error_code = "unknown"
        participant_model_dump = ""
        player_model_dump = ""
        try:
            request = record.request
            participant = get_participant_from_path_or_none(request.path)
            error_code = get_error_code(participant)
            if participant:
                # Store participant dump
                participant_model_dump = serializers.serialize("json", [participant])
                player = get_participant_last_player_or_none(participant)
                if player:
                    player_model_dump = serializers.serialize("json", [player])
        except Exception as e:
            print("CustomAdminEmailHanlder exception: ", e)

        # Traceback objects
        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None
        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)
        reporter = ExceptionReporter(request, is_email=True, *exc_info)

        # Subject
        subject = f"{record.levelname} {error_code}"

        message = ""

        if participant_model_dump:
            message += f"Participant object\n\n{participant_model_dump} \n\n\n"

        if player_model_dump:
            message += f"Player object\n\n{participant_model_dump} \n\n\n"

        message += f"Record\n\n{self.format(no_exc_record)} \n\n\n"
        message += f"Traceback\n\n{reporter.get_traceback_text()}"

        html_message = reporter.get_traceback_html()

        self.send_mail(subject, message, html_message=html_message)
