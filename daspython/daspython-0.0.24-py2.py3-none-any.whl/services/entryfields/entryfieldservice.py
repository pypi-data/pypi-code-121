from enum import Enum
from requests.api import request
from daspython.common.api import ApiMethods, Token


class DisplayType(Enum):
    NONE = 0
    FORM = 2
    TABLE = 4
    PREVIEW = 8
    PRINTER = 16
    MODALS = 32
    TEMPLATES = 64


class EntryFieldService(ApiMethods):
    def __init__(self, auth: Token):
        super().__init__(auth)

    def get_all(self, attributeId: int, displayType: DisplayType):

        api_url = f'/api/services/app/EntryField/GetAll?AttribteId={attributeId}&DisplayType={displayType.value}'
        response = self.get_data(url=api_url, request=request)
        return super()._get_entries_response(response)
