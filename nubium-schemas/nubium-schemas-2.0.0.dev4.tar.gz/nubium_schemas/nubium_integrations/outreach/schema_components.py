import typing
from nubium_schemas import dc, pdc, AvroModel

@pdc
class ProspectFields(AvroModel):
    class Meta:
        schema_doc = False

    firstName: str = ""
    lastName: str = ""
    emails: typing.List[str] = dc.field(default_factory=list)
    workPhones: typing.List[str] = dc.field(default_factory=list)
    mobilePhones: typing.List[str] = dc.field(default_factory=list)
    company: str = ""
    occupation: str = ""
    addressStreet: str = ""
    addressStreet2: str = ""
    addressCity: str = ""
    addressState: str = ""
    addressZip: str = ""
    addressCountry: str = ""