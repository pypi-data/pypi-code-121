import uuid

from jarvis_sdk.indykite.identity.v1beta1 import identity_management_api_pb2 as pb2
from jarvis_sdk.indykite.identity.v1beta1 import model_pb2 as model
from jarvis_sdk.model.digital_twin import DigitalTwinCore


def verify_digital_twin_email(self, token):
    try:
        if len(token) < 32:
            raise Exception("Token must be 32 chars or more.")
    except Exception as exception:
        print(exception)
        return None

    try:
        response = self.stub.VerifyDigitalTwinEmail(
            pb2.VerifyDigitalTwinEmailRequest(token=token)
        )
    except Exception as exception:
        print(exception)
        return None

    if not response:
        return None

    return DigitalTwinCore.deserialize(response.digital_twin)


def start_digital_twin_email_verification(self, dt_id, tenant_id, email):
    try:
        dt = uuid.UUID(dt_id, version=4)
    except Exception as exception:
        print("The digital twin is not in UUID4 format:")
        print(exception)
        return None

    try:
        tenant = uuid.UUID(tenant_id, version=4)
    except Exception as exception:
        print("The tenant id is not in UUID4 format:")
        print(exception)
        return None

    try:
        response = self.stub.StartDigitalTwinEmailVerification(
            pb2.StartDigitalTwinEmailVerificationRequest(
                digital_twin=model.DigitalTwin(
                    id=dt.bytes,
                    tenant_id=tenant.bytes
                ),
                email=email
            )
        )
    except Exception as exception:
        print(exception)
        return None

    if not response:
        return None

    return "Email was sent to: " + email
