import pytest

from cloudshell.shell.flows.connectivity.models.driver_response import (
    ConnectivityActionResult,
    DriverResponseRoot,
)


@pytest.mark.parametrize(
    ("success", "msg"), ((True, "success msg"), (False, "error msg"))
)
def test_connectivity_action_result(success, msg, action_model):
    if success:
        result = ConnectivityActionResult.success_result(action_model, msg)
        assert result.infoMessage == msg
        assert result.errorMessage == ""
    else:
        result = ConnectivityActionResult.fail_result(action_model, msg)
        assert result.infoMessage == ""
        assert result.errorMessage == msg
    assert result.success is success
    assert result.actionId == action_model.action_id
    assert result.type == action_model.type.value
    assert result.updatedInterface == action_model.action_target.name


def test_prepare_response(action_model):
    result = ConnectivityActionResult.success_result(action_model, "success msg")
    response = DriverResponseRoot.prepare_response([result])
    assert response.driverResponse.actionResults[0] == result
    assert response.json() == (
        '{"driverResponse": {"actionResults": ['
        '{"actionId": "96582265-2728-43aa-bc97-cefb2457ca44_0900c4b5-0f90-42e3-b495", '
        '"type": "removeVlan", '
        '"updatedInterface": "centos", '
        '"infoMessage": "success msg", '
        '"errorMessage": "", '
        '"success": true'
        "}]}}"
    )
