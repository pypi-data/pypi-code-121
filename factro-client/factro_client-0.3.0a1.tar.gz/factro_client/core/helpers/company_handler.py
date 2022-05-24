from typing import Optional, List
import logging


from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, Undefined

from .base_handler import BaseHandler

logger = logging.getLogger('factro_client')

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Company:
    id: str
    description: Optional[str] = ''
    city: Optional[str] = ''
    company_number: Optional[int] = ''
    email_address: Optional[str] = ''
    name: Optional[str] = ''
    phone: Optional[str] = ''
    short_name: Optional[str] = ''
    street: Optional[str] = ''
    website: Optional[str] = ''
    zip_code: Optional[str] = ''
    customer_id: Optional[str] = ''
    contact_ids: Optional[List[str]] = ''


class CompanyHandler(BaseHandler):

    def __init__(self, url: str, api_key: str):
        super(CompanyHandler, self).__init__(url, api_key)

    def get_company_by_id(self, company_id) -> Company:
        path = f"/api/core/companies/{company_id}"

        json_data = self.do_get(path)

        logger.debug(f"CompanyHandler.get_company_by_id({company_id} -> {json_data}")

        company = Company.schema().load(json_data)

        return company