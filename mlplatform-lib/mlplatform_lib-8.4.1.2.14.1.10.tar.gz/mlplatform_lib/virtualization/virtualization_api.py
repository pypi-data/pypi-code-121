from mlplatform_lib.api_client import ApiClient
from mlplatform_lib.virtualization.virtualization_http_client import VirtualizationHttpClient

class VirtualizationApi:
    def __init__(self, api_client: ApiClient = None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.virtualization_client = VirtualizationHttpClient(
            virtualization_addr=self.api_client.virtualization_addr, api_client=api_client
        )

    def download_unstructured(self, do_id: str) :
        print("Start download_unstructured in Virtualization Api")
        self.virtualization_client.download_unstructured(do_id=do_id)