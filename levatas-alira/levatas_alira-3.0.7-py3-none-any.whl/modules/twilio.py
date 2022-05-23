import logging
import os

from alira.instance import Instance
from alira.modules.module import InternalError
from alira.modules.notification import Notification

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

PIPELINE_TWILIO_MODULE_NAME = "twilio"


class Twilio(Notification):
    def __init__(
        self,
        configuration_directory: str,
        sender: str,
        recipients: list,
        template_filename: str,
        filtering: str = None,
        provider=None,
        media=None,
        **kwargs,
    ):
        super().__init__(
            configuration_directory=configuration_directory,
            module_id=PIPELINE_TWILIO_MODULE_NAME,
            filtering=filtering,
            **kwargs,
        )

        self.sender = sender
        self.recipients = recipients
        self.template_filename = template_filename
        self.attachment = None
        self.media = media
        self.provider = provider or TwilioProvider(**kwargs)

    def run(self, instance: Instance, **kwargs):
        super().run(instance, **kwargs)

        if self.filtering and not self.filtering(instance):
            logging.info(
                f"The instance didn't pass the filtering criteria. Instance: {instance}"
            )
            return {"status": "SKIPPED"}

        if self.media:
            self.attachment = instance.get_attribute(self.media, default=None)

        try:
            self.template_text = self._load_template(instance, self.template_filename)
            self.provider.send(
                sender=self.sender,
                recipients=self.recipients,
                message=self.template_text,
                attachment=self.attachment,
            )
        except FileNotFoundError as e:
            logging.exception(e)
            return {
                "status": "FAILURE",
                "message": f"Template file {self.template_filename} not found",
            }
        except Exception as e:
            logging.exception(e)
            return {
                "status": "FAILURE",
                "message": "There was an error sending the SMS notification",
            }

        return {"status": "SUCCESS"}


class TwilioProvider(object):
    def __init__(self, account_sid: str = None, auth_token: str = None, **kwargs):
        self.account_sid = account_sid or os.environ.get(
            "ALIRA_TWILIO_ACCOUNT_SID", None
        )
        self.auth_token = auth_token or os.environ.get("ALIRA_TWILIO_AUTH_TOKEN", None)

        if not self.account_sid or not self.auth_token:
            raise RuntimeError("The Twilio credentials were not specified")

    def send(
        self,
        sender: str,
        recipients: list,
        message: str,
        attachment: str = None,
        **kwargs,
    ):
        logging.info("Sending message using Twilio")

        client = Client(self.account_sid, self.auth_token)
        for phone_number in recipients:
            try:
                logging.info(
                    f"Sending message to '{phone_number}'. Message: '{message}'..."
                )
                arguments = {
                    "from_": sender,
                    "to": phone_number,
                    "body": message,
                }

                if attachment:
                    arguments["media_url"] = [attachment]

                client.messages.create(**arguments)

            except TwilioRestException as e:
                logging.exception(e)
