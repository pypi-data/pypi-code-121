from nubium_schemas import dc, pdc, AvroModel
from .schema_components import ProspectFields


@pdc
class OutreachProspectToUpsert(AvroModel):

    class Meta:
        schema_doc = False

    attributes: ProspectFields = dc.field(default_factory=ProspectFields)
    prospectID: str = ""
    eloqua_contact_id: str = ""
    is_subscribed: str = ""
    cdo_id: str = ""
    cdo_record_id: str = ""


def outreach_prospect_to_upsert_empty_dict():
    return OutreachProspectToUpsert(**{}).asdict()


outreach_prospect_to_upsert = OutreachProspectToUpsert.avro_schema_to_python()
