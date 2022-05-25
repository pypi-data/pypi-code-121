import uuid

from jarvis_sdk.cmd import helper
from jarvis_sdk.indykite.identity.v1beta1 import identity_management_api_pb2 as pb2
from jarvis_sdk.indykite.identity.v1beta1 import model_pb2 as model
from jarvis_sdk.utils.deserialize_digital_twin_with_token_info import deserialize_digital_twin_with_token_info


def get_digital_twin(self, digital_twin_id, tenant_id, fields):
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
        response = self.stub.GetDigitalTwin(
            pb2.GetDigitalTwinRequest(
                id=pb2.DigitalTwinIdentifier(
                    digital_twin=model.DigitalTwin(
                        id=digital_twin.bytes,
                        tenant_id=tenant.bytes
                    )
                ),
                properties=helper.create_property_mask(fields)
            )
        )
    except Exception as exception:
        print(exception)
        return None

    return deserialize_digital_twin_with_token_info(response)


def get_digital_twin_by_token(self, token, fields):
    try:
        if len(token) < 32:
            raise Exception("Token must be 32 chars or more.")
    except Exception as exception:
        print(exception)
        return None

    try:
        response = self.stub.GetDigitalTwin(
                pb2.GetDigitalTwinRequest(
                    id=pb2.DigitalTwinIdentifier(access_token=token),
                    properties=helper.create_property_mask(fields)
                )
        )
    except Exception as exception:
        print(exception)
        return None

    return deserialize_digital_twin_with_token_info(response)
