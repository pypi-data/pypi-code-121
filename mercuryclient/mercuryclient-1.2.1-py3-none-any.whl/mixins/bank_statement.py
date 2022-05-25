from typing import Tuple


class BankStatementMixin:
    """
    Mixin for analyzing bank statements
    """

    def request_bank_statement(
        self,
        statement_file_url: str,
        statement_bank_name: str,
        provider: str,
        profile: str,
        statement_password: str = None,
    ) -> str:
        api = "api/v1/bank_statement/"

        data = {
            "provider": provider,
            "profile": profile,
            "statement_file_url": statement_file_url,
            "statement_bank_name": statement_bank_name,
        }

        if statement_password is not None:
            data["statement_password"] = statement_password

        request_id, r = self._post_json_http_request(
            api, data=data, send_request_id=True, add_bearer_token=True
        )

        if r.status_code == 201:
            return request_id

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error while sending ID verification request. "
            "Status: {}, Response is {}".format(r.status_code, response_json)
        )

    def get_bank_statement_result(self, request_id: str) -> Tuple[str, dict]:
        api = "api/v1/bank_statement/"

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
                    "Error verifying ID. Status: {} | Message {}".format(
                        result["status"], result["message"]
                    )
                )
            return request_id, result

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error getting bank statement analysis result. "
            "Status: {}, Response is {}".format(r.status_code, response_json)
        )
