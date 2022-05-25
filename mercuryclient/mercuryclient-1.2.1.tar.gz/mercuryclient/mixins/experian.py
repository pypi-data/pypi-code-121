import time
import json
from typing import Tuple

from mercuryclient.types.experian.request import ExperianRequest


class ExperianMixin:
    """
    Mixin for registering Experian requests
    """

    def request_experian_report(
        self, request_obj: ExperianRequest, profile: str
    ) -> str:
        """
        POST a request to Mercury to Request Experian report. This posts the request to
        Mercury and returns immediately. Use the returned request ID and poll
        get_experian_response to check for report.
        You can also use fetch_experian_report which is a helper function that combines
        this api and the result api to get the result.

        :param request_obj: Object of ExperianRequest model
        :type request_obj: ExperianRequest
        :param profile: Experian profile name
        :type profile: str
        :return: Request ID
        :rtype: str
        """
        api = "api/v1/experian/"

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
            "Error while sending Experian request. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def get_experian_response(self, request_id: str) -> Tuple[str, dict]:
        """
        Get result for Experian job request at the provided request ID. You can poll
        this method to check for response. If the job is still progressing, the status
        within the response will be IN_PROGRESS and the method can continue to be polled
        until you get either a SUCCESS or FAILURE

        :param request_id: Request ID of the Experian job request
        :type request_id: str
        :return: Tuple containing request ID and job response. This response will
            contain the "status" of the job (IN_PROGRESS, SUCCESS or FAILURE), a
            "message" and a "data" key containing a dict with the bureau report
        :rtype: Tuple[str, dict]
        """
        api = "api/v1/experian/"

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
            "Error while getting Experian response. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def fetch_experian_report(
        self,
        request_obj: ExperianRequest,
        profile: str,
        max_attempts: int = 8,
        retry_backoff: int = 15,
    ) -> dict:
        """
        Generate an Experian request and get job result

        :param request_obj: Object of ExperianRequest model
        :type request_obj: ExperianRequest
        :param profile: Experian profile name
        :type profile: str
        :param max_attempts: Number of attempts to make when fetching the result,
            defaults to 8
        :type max_attempts: int, optional
        :param retry_backoff: Number of seconds to backoff when retrying to get the
            result, defaults to 15
        :type retry_backoff: int, optional
        :return: Dict containing the job result
        :rtype: dict
        """

        request_id = self.request_experian_report(request_obj, profile)

        attempts = 0
        while attempts < max_attempts:
            time.sleep(retry_backoff)
            request_id, result = self.get_experian_response(request_id)
            if result.get("status") != "IN_PROGRESS":
                return result

            retry_backoff *= 2
            attempts += 1

        raise Exception("Error while getting Experian response. Status: IN_PROGRESS")
