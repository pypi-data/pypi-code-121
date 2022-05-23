from email.message import EmailMessage
import smtplib
from string import Template

from .task_execution import TaskExecution


class EmailExecution(TaskExecution):
    def __init__(self,
                 sender,
                 recipients,
                 subject,
                 content,
                 recipients_cc=[],
                 ):
        super().__init__(name=subject)
        self.sender = sender
        if isinstance(recipients, str):
            recipients = [recipients]
        if isinstance(recipients_cc, str):
            recipients_cc = [recipients_cc]
        self.recipients = recipients
        self.recipients_cc = recipients_cc
        self.subject_template = Template(subject)
        self.content_template = Template(content)

    def bind_parameters(self, context_parameters):
        self.parameters["smtp_server"] = context_parameters["smtp_server"]
        self.subject = self.subject_template.safe_substitute(context_parameters)
        self.content = self.content_template.safe_substitute(context_parameters)

    def execute(self):
        msg = EmailMessage()

        msg['From'] = self.sender
        msg['To'] = ','.join(self.recipients)
        if self.recipients_cc:
            msg['Cc'] = ','.join(self.recipients_cc)
        msg['Subject'] = self.subject
        msg.set_content(self.content)

        #with open(file_path, 'rb') as attachment_file:
        #    attachment_bytes = attachment_file.read()
        #msg.add_attachment(attachment_bytes, maintype='text', subtype='plain', filename="Country_List.csv")

        with smtplib.SMTP(self.parameters["smtp_server"]) as server:
            server.send_message(msg)
