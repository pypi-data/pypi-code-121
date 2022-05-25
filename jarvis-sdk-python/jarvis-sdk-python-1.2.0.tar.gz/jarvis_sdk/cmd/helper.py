import json
import time
import uuid

from authlib.jose import JsonWebKey, jwt
from datetime import datetime, timedelta, timezone

from jarvis_sdk.indykite.identity.v1beta1 import attributes_pb2 as attributes
from jarvis_sdk.indykite.objects.v1beta1 import struct_pb2 as objects


def load_credentials(path):
    with open(path, 'r') as file:
        raw_content = file.read()
    return json.loads(raw_content)


def load_json(content):
    return json.loads(content)


def create_agent_jwt(credentials):
    jwk = credentials.get('privateKeyJWK')
    key = JsonWebKey.import_key(jwk)
    message = create_jwt_message(credentials)
    jwt_token = jwt.encode({
            'alg': 'ES256',
            'cty': 'JWT',
            'kid': jwk['kid']
    }, message, key)
    return jwt_token


def create_jwt_message(credentials):
    message = {
            'aud': credentials.get('appSpaceId'),
            'exp': get_int_from_datetime(datetime.now(timezone.utc) + timedelta(hours=24)),
            'iat': get_int_from_datetime(datetime.now(timezone.utc)),
            'iss': credentials.get('appAgentId'),
            'jti': str(uuid.uuid4()),
            'sub': credentials.get('appAgentId'),
    }
    return message


def get_int_from_datetime(dt):
    return int(time.mktime(dt.timetuple()))


def create_property_mask(fields):
    props = []
    print(fields)
    for f in fields:
        props.append(attributes.PropertyMask(definition=attributes.PropertyDefinition(property=f)))

    # print(props)
    return props


def create_property_batch_operations(value_dict):
    property_batch_ops = []
    for v in range(0, len(value_dict["add"]), 2):
        e = attributes.PropertyBatchOperation(
            add=attributes.Property(
                definition=attributes.PropertyDefinition(property=value_dict["add"][v]),
                object_value=objects.Value(string_value=value_dict["add"][v+1])
            )
        )
        property_batch_ops.append(e)

    for v in range(0, len(value_dict["add_by_ref"]), 2):
        e = attributes.PropertyBatchOperation(
            add=attributes.Property(
                definition=attributes.PropertyDefinition(property=value_dict["add_by_ref"][v]),
                reference_value=value_dict["add_by_ref"][v+1]
            )
        )
        property_batch_ops.append(e)

    for v in range(0, len(value_dict["replace"]), 2):
        e = attributes.PropertyBatchOperation(
            replace=attributes.Property(
                id=int(value_dict["replace"][v]),
                object_value=objects.Value(string_value=value_dict["replace"][v+1])
            )
        )
        property_batch_ops.append(e)

    for v in range(0, len(value_dict["replace_by_ref"]), 2):
        e = attributes.PropertyBatchOperation(
            replace=attributes.Property(
                id=int(value_dict["replace_by_ref"][v]),
                reference_value=value_dict["replace_by_ref"][v + 1]
            )
        )
        property_batch_ops.append(e)

    for v in range(0, len(value_dict["remove"])):
        e = attributes.PropertyBatchOperation(
            remove=attributes.Property(
                id=value_dict["remove"][v]
            )
        )
        property_batch_ops.append(e)

    return property_batch_ops
