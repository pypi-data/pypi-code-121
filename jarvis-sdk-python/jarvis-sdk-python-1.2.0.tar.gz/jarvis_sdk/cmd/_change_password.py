import uuid

from jarvis_sdk.indykite.identity.v1beta1 import identity_management_api_pb2 as pb2
from jarvis_sdk.indykite.identity.v1beta1 import model_pb2 as model


def change_password(self, token, new_password):
    try:
        if len(token) < 32:
            raise Exception("Token must be 32 chars or more.")
    except Exception as exception:
        print(exception)
        return None

    try:
        response = self.stub.ChangePassword(
            pb2.ChangePasswordRequest(
                token=token,
                password=new_password,
                ignore_policy=2
            )
        )
    except Exception as exception:
        print(exception)
        return None

    if not response:
        return None

    return "The password has been changed successfully"


def change_password_of_user(self, digital_twin_id, tenant_id, new_password):
    try:
        digital_twin = uuid.UUID(digital_twin_id, version=4)
    except Exception as exception:
        print("The digital twin is not in UUID4 format:")
        print(exception)
        return None

    try:
        tenant = uuid.UUID(tenant_id, version=4)
    except Exception as exception:
        print("The digital twin is not in UUID4 format:")
        print(exception)
        return None

    try:
        response = self.stub.ChangePassword(
            pb2.ChangePasswordRequest(
                digital_twin=model.DigitalTwin(
                    id=digital_twin.bytes,
                    tenant_id=tenant.bytes
                ),
                password=new_password
            )
        )
    except Exception as exception:
        print(exception)
        return None

    if not response:
        return None

    return "The password has been changed successfully"
