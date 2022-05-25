from django.conf import settings

from directory_api_client.base import AbstractAPIClient
from directory_api_client.buyer import BuyerAPIClient
from directory_api_client.company import CompanyAPIClient
from directory_api_client.dataservices import DataServicesAPIClient
from directory_api_client.enrolment import EnrolmentAPIClient
from directory_api_client.exporting import ExportingAPIClient
from directory_api_client.exportplan import ExportPlanAPIClient
from directory_api_client.notifications import NotificationsAPIClient
from directory_api_client.personalisation import PersonalisationAPIClient
from directory_api_client.supplier import SupplierAPIClient

url_ping = '/healthcheck/ping/'


class DirectoryAPIClient(AbstractAPIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enrolment = EnrolmentAPIClient(*args, **kwargs)
        self.company = CompanyAPIClient(*args, **kwargs)
        self.supplier = SupplierAPIClient(*args, **kwargs)
        self.buyer = BuyerAPIClient(*args, **kwargs)
        self.notifications = NotificationsAPIClient(*args, **kwargs)
        self.exporting = ExportingAPIClient(*args, **kwargs)
        self.exportplan = ExportPlanAPIClient(*args, **kwargs)
        self.personalisation = PersonalisationAPIClient(*args, **kwargs)
        self.dataservices = DataServicesAPIClient(*args, **kwargs)

    def ping(self):
        return self.get(url=url_ping)


api_client = DirectoryAPIClient(
    base_url=settings.DIRECTORY_API_CLIENT_BASE_URL,
    api_key=settings.DIRECTORY_API_CLIENT_API_KEY,
    sender_id=settings.DIRECTORY_API_CLIENT_SENDER_ID,
    timeout=settings.DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT,
)
