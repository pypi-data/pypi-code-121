from typing import Dict, List

from pydantic import BaseModel

from .connectivity_model import ConnectivityActionModel


class ConnectivityActionResult(BaseModel):
    actionId: str
    type: str  # noqa: A003
    updatedInterface: str
    infoMessage: str = ""
    errorMessage: str = ""
    success: bool = True

    @staticmethod
    def _action_dict(action: ConnectivityActionModel) -> Dict[str, str]:
        return {
            "actionId": action.action_id,
            "type": action.type.value,
            "updatedInterface": action.action_target.name,
        }

    @classmethod
    def success_result(
        cls, action: ConnectivityActionModel, msg: str
    ) -> "ConnectivityActionResult":
        return cls(**cls._action_dict(action), infoMessage=msg)

    @classmethod
    def success_result_vm(
        cls, action: ConnectivityActionModel, msg: str, mac_address: str
    ) -> "ConnectivityActionResult":
        inst = cls.success_result(action, msg)
        inst.updatedInterface = mac_address
        return inst

    @classmethod
    def fail_result(
        cls, action: ConnectivityActionModel, msg: str
    ) -> "ConnectivityActionResult":
        return cls(**cls._action_dict(action), errorMessage=msg, success=False)


class DriverResponse(BaseModel):
    actionResults: List[ConnectivityActionResult]


class DriverResponseRoot(BaseModel):
    driverResponse: DriverResponse

    @classmethod
    def prepare_response(cls, action_results: List[ConnectivityActionResult]):
        return cls(driverResponse=DriverResponse(actionResults=action_results))
