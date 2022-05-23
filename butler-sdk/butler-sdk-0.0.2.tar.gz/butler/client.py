from pprint import pprint
import time
from butler.api.queues_api import QueuesApi

from butler.api_client import ApiClient
from butler.configuration import Configuration
from butler.model.document_status import DocumentStatus
from butler.model.extraction_results_dto import ExtractionResultsDto
from butler.model.paginated_extraction_results_dto import PaginatedExtractionResultsDto


class Client(ApiClient):
    def __init__(self, api_key: str) -> None:
        super().__init__(
            configuration = Configuration(
                access_token = api_key
            )
        )

    def extract_file(self, file_path: str, queue_id: str) -> ExtractionResultsDto:
        """
        Uploads a supported file (PDF, PNG, and JPG) to the Butler API and fetches results

        Limitations: Function times out in 30 seconds. Lower the number of pages in your fil
        if it times out.
        """
        upload_id = None
        with open(file_path, 'rb') as f:
            upload_id = QueuesApi(self).upload_documents_to_queue(
                queue_id = queue_id,
                files = [f]
            ).upload_id

        for i in range(0, 30):
            res = QueuesApi(self).get_extraction_results(
                queue_id = queue_id,
                upload_id = upload_id
            ).items[0]

            if str(res.document_status) == 'Completed':
                return res

            time.sleep(1)
