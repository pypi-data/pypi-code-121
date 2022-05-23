import os
import logging
import requests

from alira.email.smtp import SMTP
from alira.instance import Instance
from alira.modules.module import InternalError
from alira.modules.notification import Notification

PIPELINE_EMAIL_MODULE_NAME = "email"


class Email(Notification):
    def __init__(
        self,
        configuration_directory: str,
        sender: str,
        recipients: list,
        subject: str,
        template_filename: str,
        filtering: str = None,
        files: list = None,
        files_directory: str = None,
        relay=None,
        **kwargs,
    ):
        super().__init__(
            configuration_directory=configuration_directory,
            module_id=PIPELINE_EMAIL_MODULE_NAME,
            filtering=filtering,
            **kwargs,
        )

        self.sender = sender
        self.recipients = recipients
        self.template_filename = template_filename
        self.subject = subject
        self.files = files
        self.files_directory = files_directory or "files"

        if relay is None:
            relay = "smtp"

        if isinstance(relay, str):
            if relay == "smtp":
                self.relay = SMTPRelay(
                    configuration_directory=configuration_directory,
                    sender=sender,
                    recipients=recipients,
                    subject=subject,
                    files_directory=files_directory,
                    files=files,
                    **kwargs,
                )
            elif relay == "rest":
                self.relay = RestRelay(
                    sender=sender, recipients=recipients, subject=subject, **kwargs
                )
            else:
                raise InternalError(f"Unknown relay '{relay}'")
        else:
            self.relay = relay

    def run(self, instance: Instance, rest_authentication=None, **kwargs) -> dict:
        super().run(instance, **kwargs)

        if self.filtering and not self.filtering(instance):
            logging.info(
                f"The instance didn't pass the filtering criteria. Instance: {instance}"
            )
            return {"status": "SKIPPED"}

        try:
            self.template = self._load_template(instance, self.template_filename)
            response = self.relay.send(
                instance=instance,
                message=self.template,
                rest_authentication=rest_authentication,
                **kwargs,
            )

            if not response[0]:
                return {
                    "status": "FAILURE",
                    "message": ("Failed to send email notification. " f"{response[1]}"),
                }
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
                "message": "There was an error sending the email notification",
            }

        return {"status": "SUCCESS"}


class SMTPRelay:
    def __init__(
        self,
        configuration_directory: str,
        sender: str,
        recipients: list,
        subject: str,
        files_directory: str = None,
        files: str = None,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_username: str = None,
        smtp_password: str = None,
        smtp=None,
        **kwargs,
    ):
        self.configuration_directory = configuration_directory
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.files_directory = files_directory or "files"
        self.files = files

        try:
            self.smtp_host = smtp_host or os.environ["ALIRA_SMTP_HOST"]
            self.smtp_port = smtp_port or int(os.environ["ALIRA_SMTP_PORT"])
            self.smtp_username = smtp_username or os.environ.get(
                "ALIRA_SMTP_USERNAME", None
            )
            self.smtp_password = smtp_password or os.environ.get(
                "ALIRA_SMTP_PASSWORD", None
            )
        except Exception as e:
            message = (
                "Error loading SMTP configuration from environment variables. "
                "Make sure the ALIRA_SMTP_HOST and ALIRA_SMTP_PORT are "
                "correctly set."
            )
            logging.error(message)
            raise InternalError(message)

        self.smtp = smtp or SMTP(
            self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password
        )

    def send(self, instance: Instance, message: str, **kwargs):
        default_files = instance.files if instance.files else None
        if self.files:
            filenames = instance.get_attribute(self.files, default=default_files)
            # The `files` field might be pointing to field containing a single
            # file. In that case, we need to convert it to a list.
            if filenames and not isinstance(filenames, list):
                filenames = [filenames]
        else:
            filenames = default_files

        attachments = []
        if filenames:
            for filename in filenames:
                filename = os.path.join(
                    self.configuration_directory, self.files_directory, filename
                )
                attachments.append(filename)

        self.smtp.send(
            sender=self.sender,
            recipients=self.recipients,
            subject=self.subject,
            message=message,
            attachments=attachments,
        )

        return True, None


class RestRelay:
    def __init__(
        self,
        sender: str,
        recipients: list,
        subject: str,
        **kwargs,
    ):
        self.sender = sender
        self.recipients = recipients
        self.subject = subject

    def send(self, instance: Instance, message: str, rest_authentication, **kwargs):
        if rest_authentication is None:
            return False, "The rest authentication dependency was not configured."

        access_token = rest_authentication.get_access_token()

        url = "/".join(
            map(
                lambda x: str(x).rstrip("/"),
                [rest_authentication.service, "email", instance.id],
            )
        )

        data = {
            "subject": self.subject,
            "message": message,
            "recipients": self.recipients,
        }

        response = requests.post(
            url=url,
            json=data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code == 200:
            return True, None

        return False, (
            f"Server error: {response.status_code} - {response.json()['message']}"
        )
