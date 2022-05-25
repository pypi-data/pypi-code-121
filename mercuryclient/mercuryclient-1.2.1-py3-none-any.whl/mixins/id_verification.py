import json
from typing import Tuple

from mercuryclient.types.id_verification.enums import IDTypes
from mercuryclient.types.id_verification.request import PassportDetails


class IDVerificationMixin:
    """
    Mixin for verifying IDs
    """

    def request_verify_id(
        self,
        id_type: IDTypes,
        id_number: str,
        provider: str,
        profile: str,
        passport_details: PassportDetails = None,
    ) -> str:
        api = "api/v1/id_verification/"

        try:
            IDTypes(id_type)
        except ValueError:
            raise Exception(f"{id_type} is not a valid id_type")

        data = {
            "provider": provider,
            "profile": profile,
            "id_type": id_type,
            "id_number": id_number,
        }

        if id_type == IDTypes.PASSPORT.value:
            if not passport_details:
                raise Exception("passport_details required for PASSPORT ID Type")

            passport_details_dict = json.loads(
                passport_details.json(exclude_unset=True)
            )
            data["passport_details"] = passport_details_dict

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
            "Error while sending ID verification request. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def get_verify_id_result(self, request_id: str) -> Tuple[str, dict]:
        api = "api/v1/id_verification/"

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
            "Error getting ID Verification result. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )
