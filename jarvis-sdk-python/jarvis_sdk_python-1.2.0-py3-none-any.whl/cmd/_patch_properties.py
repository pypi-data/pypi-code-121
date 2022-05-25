import uuid

from jarvis_sdk.cmd import helper
from jarvis_sdk.indykite.identity.v1beta1 import identity_management_api_pb2 as pb2
from jarvis_sdk.indykite.identity.v1beta1 import model_pb2 as model


def patch_properties(self, digital_twin_id, tenant_id, fields_in_dict):
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
        response = self.stub.PatchDigitalTwin(
            pb2.PatchDigitalTwinRequest(
                id=pb2.DigitalTwinIdentifier(
                    digital_twin=model.DigitalTwin(
                        id=digital_twin.bytes,
                        tenant_id=tenant.bytes
                    )
                ),
                operations=helper.create_property_batch_operations(fields_in_dict)
            )
        )
    except Exception as exception:
        print(exception)
        return None

    if not response:
        return None

    return response


def patch_properties_by_token(self, token, fields_in_dict):
    try:
        if len(token) < 32:
            raise Exception("Token must be 32 chars or more.")
    except Exception as exception:
        print(exception)
        return None

    try:
        # identifier = pb2.DigitalTwinIdentifier()
        # identifier.access_token = token

        response = self.stub.PatchDigitalTwin(
            pb2.PatchDigitalTwinRequest(
                id=pb2.DigitalTwinIdentifier(access_token=token),
                operations=helper.create_property_batch_operations(fields_in_dict)
            )
        )
    except Exception as exception:
        print(exception)
        return None

    if not response:
        return None

    return "The patch operation was success: " + str(response)
