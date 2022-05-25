class SMSMixin:
    """
    Mixin for sending emails
    """

    def send_sms(self, recipient, message, provider, profile):
        """
        POST a request to Mercury to send an SMS

        :param recipient: Phone number of recipients
        :param message: SMS message to be sent
        :param provider: Name of SMS Provider
        :param profile: Profile name from which to send SMS
        :return: (request_id, status)
        """
        api = "api/v1/sms/"

        data = {
            "provider": provider,
            "profile": profile,
            "recipient": recipient,
            "message": message,
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
            "Error while sending SMS. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def get_sms_result(self, request_id):
        """
        Get result for SMS request at the provided request ID. You can poll this method
        to check for response. If the job is still progressing, the status within the
        response will be IN_PROGRESS and the method can continue to be polled until you
        get either a SUCCESS or FAILURE

        :param request_id: Request ID of the SMS request
        :type request_id: str
        :return: Dict containing request ID, status and job response within "response".
            This response will contain the "status" of the job (IN_PROGRESS, SUCCESS or
            FAILURE), a "message" and a "data" key containing a dict with the bureau
            report
        :rtype: dict
        """
        api = "api/v1/sms/"

        request_id, r = self._get_json_http_request(
            api,
            headers={"X-Mercury-Request-Id": request_id},
            send_request_id=False,
            add_bearer_token=True,
        )

        if r.status_code == 200:
            result = r.json()
            if result["status"] == "FAILURE":
                raise Exception(
                    "Error sending SMS. Status: {} | Message {}".format(
                        result["status"], result["message"]
                    )
                )
            return {"request_id": request_id, "status": result["status"]}

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error getting SMS result. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )
