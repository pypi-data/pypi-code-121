from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

import iopool
from iopool.const import ROUTES
# from iopool.errors import WrongApiKeyError

if TYPE_CHECKING:
    from respx import MockRouter


# def test_missing_api_key(requests_mock) -> None:  # type: ignore
#     """Test generic session."""
#     requests_mock.post(
#         FLIPR_AUTH_URL,
#         json={
#             "access_token": "abcd-dummy_token_value",
#             "token_type": "bearer",
#             "expires_in": 23327999,
#             "refresh_token": "dummy_refresh_token",
#         },
#     )

#     session = FliprClientSession(USERNAME, PASSWORD)

#     requests_mock.get(
#         f"{FLIPR_API_URL}/modules",
#         json=[
#             {
#                 "ActivationKey": "12345",
#                 "IsSuspended": False,
#                 "Status": {
#                     "Comment": None,
#                     "DateTime": "2020-04-13T14:26:53.563",
#                     "Status": "Activated",
#                 },
#                 "BatteryPlugDate": "2019-07-01T00:00:00",
#                 "Comments": None,
#                 "NoAlertUnil": "2000-01-01T00:00:00",
#                 "Serial": "AB256C",
#                 "PAC": "123456B",
#                 "ResetsCounter": 4,
#                 "SigfoxStatus": "Activated",
#                 "OffsetOrp": 0.0,
#                 "OffsetTemperature": 0.0,
#                 "OffsetPh": 0.0,
#                 "OffsetConductivite": 0,
#                 "IsForSpa": False,
#                 "Version": 3,
#                 "LastMeasureDateTime": "2021-02-01T07:40:23.663",
#                 "CommercialType": {"Id": 2, "Value": "Pro"},
#                 "SubscribtionValidUntil": 1565947747,
#                 "ModuleType_Id": 1,
#                 "Eco_Mode": 0,
#                 "IsSubscriptionValid": True,
#             }
#         ],
#     )

#     resp = session.rest_request("GET", "modules")
#     assert resp.status_code == 200

#     requests_mock.get(f"{FLIPR_API_URL}/dumb", exc=RequestException)

#     with pytest.raises(RequestException):
#         resp = session.rest_request("GET", "dumb")



@pytest.mark.asyncio
async def test_wrong_api_key(get, respx_mock: MockRouter) -> None:
    """Test exception raised with wrong token."""
    respx_mock.get(ROUTES.url_for("pools")).respond(json={"message": "Forbidden"}, status_code=403)

    with pytest.raises(iopool.WrongApiKeyError):
        await get("pools")
