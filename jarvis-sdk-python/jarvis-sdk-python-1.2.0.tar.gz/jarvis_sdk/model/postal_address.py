from jarvis_sdk.indykite.identity.v1beta1.model_pb2 import PostalAddress as PostalAddressPb
from google.protobuf.json_format import MessageToDict


class PostalAddress:
    @classmethod
    def deserialize(cls, message):
        if not message.Is(PostalAddressPb.DESCRIPTOR):
            return None

        msg_dict = MessageToDict(message)
        return PostalAddress(
            msg_dict.get('addressType', ''),
            msg_dict.get('addressCountry', ''),
            msg_dict.get('addressCountryCode', ''),
            msg_dict.get('addressLocality', ''),
            msg_dict.get('addressRegion', ''),
            msg_dict.get('postOfficeBoxNumber', ''),
            msg_dict.get('postalCode', ''),
            msg_dict.get('streetAddress', ''),
            msg_dict.get('formatted', '')
        )

    def __init__(
        self,
        address_type,
        address_country,
        address_country_code,
        address_locality,
        address_region,
        post_office_box_number,
        postal_code,
        street_address,
        formatted
    ):
        self.addressType = address_type
        self.addressCountry = address_country
        self.addressCountryCode = address_country_code
        self.addressLocality = address_locality
        self.addressRegion = address_region
        self.postOfficeBoxNumber = post_office_box_number
        self.postalCode = postal_code
        self.streetAddress = street_address
        self.formatted = formatted

    def __str__(self):
        if self.formatted:
            return self.formatted
        else:
            return '<Postal Address object>'
