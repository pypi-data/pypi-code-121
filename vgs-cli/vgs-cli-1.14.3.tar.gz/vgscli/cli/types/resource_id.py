import click

from vgscli.id_generator import base58_to_uuid, uuid_to_base58


class ResourceId:
    """
    ID of a VGS resource as shown on the dashboard (e.g., ACtELxZxTcXrAMk2Gp8Qp5yh).
    """

    def __init__(self, prefix: str, uuid_string: str):
        self.uuid = uuid_string
        self._base58 = uuid_to_base58(uuid_string, prefix)

    @property
    def base58(self) -> str:
        return self._base58

    @staticmethod
    def decode_base58(prefix: str, base58_string: str) -> 'ResourceId':
        uuid_string = base58_to_uuid(base58_string)
        return ResourceId(prefix, uuid_string)


class ResourceIdParamType(click.ParamType):
    name = 'resource_id'

    def __init__(self, **kwargs):
        self.prefix = kwargs.get('prefix', '')

    def convert(self, value: str, param, ctx) -> ResourceId:
        try:
            if value.startswith(self.prefix):
                base58_string = value[len(self.prefix):]
                return ResourceId.decode_base58(self.prefix, base58_string)

            return ResourceId(self.prefix, value)
        except ValueError:
            self.fail(f'{value!r} is not a valid organization ID', param, ctx)
