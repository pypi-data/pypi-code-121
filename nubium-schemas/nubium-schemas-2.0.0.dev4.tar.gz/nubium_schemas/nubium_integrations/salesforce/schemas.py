from nubium_schemas import dc, pdc, AvroModel

from .schema_components import SalesforceRecord


@pdc
class SalesforceRecordData(AvroModel):
    salesforce_record_data: SalesforceRecord = dc.field(default_factory=SalesforceRecord)

    class Meta:
        schema_doc = False
        alias_nested_items = {
            "salesforce_record": "SalesforceRecord"
        }


def salesforce_record_data_empty_dict():
    return SalesforceRecordData(**{}).asdict()


salesforce_record_data = SalesforceRecordData.avro_schema_to_python()
