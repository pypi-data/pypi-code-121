import json
from typing import List, Tuple

from fiddler.libs.http_client.client import Response
from fiddler.utils import logging
from fiddler.v2.utils.exceptions import FiddlerAPIException

logger = logging.getLogger(__name__)


class BaseResponseHandler:
    def __init__(self, response: Response) -> None:
        if response.headers.get('Content-Type') != 'application/json':
            raise FiddlerAPIException(
                status_code=response.status_code,
                error_code=response.status_code,
                message=f'Invalid response content-type. {response.status_code}:{response.body}',
                errors=[],
            )
        self.response = response
        logger.debug(self.response.body)

    def get_data(self) -> dict:
        dict_response = json.loads(self.response.body).get('data')
        dict_response.pop('kind', None)
        dict_response.pop('created_by', None)
        dict_response.pop('updated_by', None)
        dict_response.pop('created_at', None)
        dict_response.pop('updated_at', None)
        return dict_response

    def get_status_code(self) -> int:
        return self.response.status_code


class PaginatedResponseHandler(BaseResponseHandler):
    '''
    Handle fiddler OAS's standard Paginated response
    '''

    def get_pagination_details_and_items(self) -> Tuple[dict, List[dict]]:
        data = self.get_data()
        items = data.pop('items')
        return data, items


class APIResponseHandler(BaseResponseHandler):
    '''
    Handle fiddler OAS's standard API Response
    '''


class JobResponseHandler(BaseResponseHandler):
    def __init__(self, response: Response) -> None:
        super().__init__(response)
        data = self.get_data()
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.status = data.get('status')
        self.progress = data.get('progress')
        self.error_message = data.get('error_message')
        self.extras = data.get('extras')
