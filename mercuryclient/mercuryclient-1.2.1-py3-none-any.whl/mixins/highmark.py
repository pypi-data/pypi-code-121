import json
import time
from typing import Tuple

from mercuryclient.types.highmark.request import HighmarkRequest


class HighmarkMixin:
    """
    Mixin for registering Highmark requests
    """

    def request_highmark_report(
        self, request_obj: HighmarkRequest, profile: str
    ) -> str:
        """
        POST a request to Mercury to Request Highmark report. This posts the request to
        Mercury and returns immediately. Use the returned request ID and poll
        get_highmark_response to check for report.
        You can also use fetch_highmark_report which is a helper function that combines
        this api and the result api to get the result.

        :param application_data: Dict containing application data to get Highmark report
        :type application_data: dict
        :param profile: Highmark profile name
        :type profile: str
        :return: Request ID
        :rtype: str
        """
        api = "api/v1/highmark/"

        # It is necessary to JSON encode the models to serialize the enums and datetime
        # formats into strings
        request_dict = json.loads(request_obj.json(exclude_unset=True))
        request_dict["profile"] = profile

        request_id, r = self._post_json_http_request(
            api, data=request_dict, send_request_id=True, add_bearer_token=True
        )

        if r.status_code == 201:
            return request_id

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error while sending Highmark request. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def get_highmark_response(self, request_id: str) -> Tuple[str, dict]:
        """
        Get result for Highmark job request at the provided request ID. You can poll
        this method to check for response. If the job is still progressing, the status
        within the response will be IN_PROGRESS and the method can continue to be polled
        until you get either a SUCCESS or FAILURE

        :param request_id: Request ID of the Highmark job request
        :type request_id: str
        :return: Tuple containing request ID and job response. This response will
            contain the "status" of the job (IN_PROGRESS, SUCCESS or FAILURE), a
            "message" and a "data" key containing a dict with the bureau report
        :rtype: Tuple[str, dict]
        """
        api = "api/v1/highmark/"

        request_id, r = self._get_json_http_request(
            api,
            headers={"X-Mercury-Request-Id": request_id},
            send_request_id=False,
            add_bearer_token=True,
        )

        if r.status_code == 200:
            return request_id, r.json()

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error while getting Highmark response. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def fetch_highmark_report(
        self,
        request_obj: HighmarkRequest,
        profile: str,
        max_attempts: int = 5,
        retry_backoff: int = 11,
    ) -> dict:
        """
        Generate an Highmark request and get job result

        :param request_obj: Object of HighmarkRequest model
        :type request_obj: HighmarkRequest
        :param profile: Highmark profile name
        :type profile: str
        :param max_attempts: Number of attempts to make when fetching the result,
            defaults to 5
        :type max_attempts: int, optional
        :param retry_backoff: Number of seconds to backoff when retrying to get the
            result, defaults to 11
        :type retry_backoff: int, optional
        :return: Dict containing the job result
        :rtype: dict
        """

        request_id = self.request_highmark_report(request_obj, profile)

        attempts = 0
        while attempts < max_attempts:
            time.sleep(retry_backoff)
            request_id, result = self.get_highmark_response(request_id)
            if result.get("status") != "IN_PROGRESS":
                return result

            retry_backoff *= 2
            attempts += 1

        raise Exception("Error while getting Highmark response. Status: IN_PROGRESS")
