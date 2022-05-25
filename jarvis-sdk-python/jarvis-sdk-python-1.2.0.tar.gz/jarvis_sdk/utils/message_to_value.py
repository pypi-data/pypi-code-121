'''Converts gRPC object to a value'''
from jarvis_sdk.indykite.identity.v1beta1.model_pb2 import PostalAddress as PostalAddressPb
from jarvis_sdk.model.postal_address import PostalAddress

def object_to_value(grpc_object):
    '''Converts gRPC object to a value'''

    if grpc_object.HasField('null_value'):
        return grpc_object.null_value

    if grpc_object.HasField('bool_value'):
        return grpc_object.bool_value

    if grpc_object.HasField('integer_value'):
        return grpc_object.integer_value

    if grpc_object.HasField('unsigned_integer_value'):
        return grpc_object.unsigned_integer_value

    if grpc_object.HasField('double_value'):
        return grpc_object.double_value

    if grpc_object.HasField('value_time'):
        return grpc_object.value_time

    if grpc_object.HasField('duration_value'):
        return grpc_object.duration_value

    if grpc_object.HasField('identifier_value'):
        return grpc_object.identifier_value

    if grpc_object.HasField('string_value'):
        return grpc_object.string_value

    if grpc_object.HasField('bytes_value'):
        return grpc_object.bytes_value

    if grpc_object.HasField('geo_point_value'):
        return grpc_object.geo_point_value

    if grpc_object.HasField('any_value'):
        if grpc_object.any_value.Is(PostalAddressPb.DESCRIPTOR):
            return PostalAddress.deserialize(grpc_object.any_value)
        return grpc_object.any_value

    if grpc_object.HasField('array_value'):
        return list(map(object_to_value, grpc_object.array_value.values))

    if grpc_object.HasField('map_value'):
        fields = grpc_object.map_value.fields
        keys = fields.keys()
        mapped = {}
        for key in keys:
            mapped[key] = object_to_value(fields[key])
        return mapped

    return None
