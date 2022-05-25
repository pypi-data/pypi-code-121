class MailMixin:
    """
    Mixin for sending emails
    """

    def send_mail(self, recipients, subject, body, provider, profile):
        """
        Send email using the mercury service

        :param recipients: List of recipients
        :param subject: Subject of the email
        :param body: Body of the email.
        :param provider: Either 'ses' or 'mailgun'
        :param profile: An existing profile in Mercury. The profile has to correspond
        to the provider.
        :return: (request_id, status)
        """
        api = "api/v1/mail/"

        data = {
            "provider": provider,
            "profile": profile,
            "subject": subject,
            "recipients": recipients,
            "message": body,
        }

        request_id, r = self._post_json_http_request(
            api, data=data, send_request_id=True, add_bearer_token=True
        )

        if r.status_code == 201:
            return {"request_id": request_id, "status": "Success"}

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error while sending mail. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )
