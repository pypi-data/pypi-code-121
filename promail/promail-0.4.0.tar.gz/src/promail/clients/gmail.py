"""Gmail Mail Client."""
import base64
import os.path
from typing import List, Optional

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore

from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore


from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore


from promail.clients.email_manager import InBoundManager, OutBoundManager
from promail.core.embedded_attachments import EmbeddedAttachments


class GmailClient(OutBoundManager, InBoundManager):
    """Gmail Client."""

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
    ]

    def __init__(
        self,
        account: str,
        token_path: str = "",
        credentials: str = "",
        clear_token: bool = False,
    ) -> None:  # ignore
        """Initiates Gmail Client.

        Args:
            clear_token: Should class clear access token on exit
            account: Gmail Email Address
            token_path: Path of Gmail token. Leave blank for default
            credentials: Location of Gmail API Credentials.

                Leave Blank to use promail's credentials.
                Promail is shipped with credentials, however there
                is a daily maximum of 1 Billion Actions
                shared amongst all users of the software.

                To keep this pool available we recommend that for heavy or
                production uses you create your own key, so that
                we don't exhaust current resources.
                The Gmail API is free so there are no cost implications.


        """
        super(GmailClient, self).__init__(account)
        sanitized_account: str = "".join(x for x in account if x.isalnum())
        self._token_path: str = token_path or os.path.join(
            os.getcwd(),
            ".credentials",
            "gmail",
            f"{sanitized_account}.json",
        )
        print(self._token_path)
        self.gmail_credentials: str = credentials or (
            os.path.dirname(os.path.realpath(__file__))
            + r"\\..\\..\\.credentials/gmail_credentials.json"
        )
        self.login()
        self._clear_token = clear_token

    def login(self):
        """Logs into Gmail using OAuth and saves a token for later use."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self._token_path):
            creds = Credentials.from_authorized_user_file(
                self._token_path, GmailClient.SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.gmail_credentials, GmailClient.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run

            # folder doesn't exist create it
            if not os.path.exists(os.path.dirname(self._token_path)):
                os.makedirs(os.path.dirname(self._token_path))

            with open(self._token_path, "w") as token:
                token.write(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)
        return self.service

    def send_email(
        self,
        recipients: str = "",
        cc: str = "",
        bcc: str = "",
        subject: str = "",
        htmltext: str = "",
        plaintext: str = "",
        embedded_attachments: Optional[List[EmbeddedAttachments]] = None,
        attachements: Optional[list] = None,
    ) -> None:
        """Send email."""
        msg = self.create_message(
            recipients,
            cc,
            bcc,
            subject,
            htmltext,
            plaintext,
            embedded_attachments,
            attachements,
        )

        raw_data = base64.urlsafe_b64encode(msg.as_bytes())
        raw = raw_data.decode()
        try:
            # by specifying "me" it will always send from logged-in user
            message = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw})
                .execute()
            )
            print("Message Id: %s" % message["id"])
            return message
        except HttpError as error:
            print("An error occurred: %s" % error)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """If clear token flag has been set will delete token on exit."""
        if self._clear_token:
            os.remove(self._token_path)
