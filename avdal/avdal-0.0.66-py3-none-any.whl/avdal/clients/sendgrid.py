import os
import json
import hashlib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendgridEmailer:
    def __init__(self, api_key: str,
                 deadletter_dir: str = None,
                 liveletter_dir: str = None,
                 logger=None,
                 noop: bool = False):

        assert api_key, "API key is required"

        self.client = SendGridAPIClient(api_key)
        self.deadletter_dir = deadletter_dir
        self.liveletter_dir = liveletter_dir
        self.logger = logger
        self.noop = noop

        os.makedirs(self.deadletter_dir, exist_ok=True)
        os.makedirs(self.liveletter_dir, exist_ok=True)

    def save_letter(self, email: Mail, dir: str) -> None:
        encoded = json.dumps(email.get(), sort_keys=True).encode()
        hash = hashlib.md5(encoded).hexdigest()
        filename = os.path.join(dir, f"{hash}.json")

        try:
            with open(filename, "w") as f:
                json.dump(email.get(), f, indent=4)
        except Exception as e:
            if self.logger:
                self.logger.error(e)

    def send_email(self, sender, receiver, subject, body) -> bool:
        if self.logger:
            self.logger.info(f"Sending email. Body=[{body}]")

        email = Mail(from_email=sender,
                     to_emails=receiver,
                     subject=subject,
                     plain_text_content=body)

        try:
            if not self.noop:
                self.client.send(email)
            if self.logger:
                self.logger.info(f"Sent an email.")
            if self.liveletter_dir:
                self.save_letter(email, self.liveletter_dir)

            return True
        except Exception as e:
            if self.deadletter_dir:
                self.save_letter(email, self.deadletter_dir)
            if self.logger:
                self.logger.error(e)

            return False
