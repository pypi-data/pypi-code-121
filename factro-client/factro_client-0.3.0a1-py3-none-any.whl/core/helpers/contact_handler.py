from typing import Optional
import logging


from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, Undefined

from .base_handler import BaseHandler

logger = logging.getLogger('factro_client')

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Contact:
    id: str
    company_id: str
    description: Optional[str] = ''
    city: Optional[str] = ''
    email_address: Optional[str] = ''
    phone: Optional[str] = ''
    street: Optional[str] = ''
    zip_code: Optional[str] = ''
    first_name: Optional[str] = ''
    last_name: Optional[str] = ''
    mobile_phone: Optional[str] = ''
    salutation: Optional[str] = ''

class ContactHandler(BaseHandler):

    def __init__(self, url: str, api_key: str):
        super(ContactHandler, self).__init__(url, api_key)

    def get_contact_by_id(self, contact_id) -> Contact:
        path = f"/api/core/contacts/{contact_id}"

        json_data = self.do_get(path)

        logger.debug(f"ContactHandler.get_contact_by_id({contact_id} -> {json_data}")

        contact = Contact.schema().load(json_data)

        return contact