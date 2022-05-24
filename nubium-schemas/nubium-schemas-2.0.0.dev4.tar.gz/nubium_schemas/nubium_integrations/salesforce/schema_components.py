import typing

from nubium_schemas import dc, pdc, AvroModel


@pdc
class SalesforceRecord(AvroModel):
    class Meta:
        schema_doc = False

    id: str = ""
    field_map: typing.Dict[str, str] = dc.field(default_factory=dict)
