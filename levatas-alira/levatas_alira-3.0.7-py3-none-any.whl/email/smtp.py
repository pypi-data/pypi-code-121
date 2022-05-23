import os
import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication


class SMTP:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password

    def send(
        self,
        sender: str,
        recipients: list,
        subject: str,
        message: str,
        attachments: list,
    ):
        email_message = MIMEMultipart()
        email_message["From"] = sender
        email_message["To"] = ", ".join(recipients)
        email_message["Subject"] = subject
        email_message.attach(MIMEText(message, "html"))

        if attachments:
            for attachment in attachments:
                with open(attachment, "rb") as f:
                    if (
                        attachment.endswith(".jpg")
                        or attachment.endswith(".jpeg")
                        or attachment.endswith(".png")
                    ):
                        file_attachment = MIMEImage(
                            f.read(), name=os.path.basename(attachment)
                        )
                    else:
                        file_attachment = MIMEApplication(f.read())
                        file_attachment.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(attachment)}",
                        )

                email_message.attach(file_attachment)

        email_string = email_message.as_string()

        if self.port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                server.login(self.username, self.password)
                server.sendmail(sender, recipients, email_string)
        else:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.username and self.password:
                    server.login(self.username, self.password)

                server.sendmail(sender, recipients, email_string)
