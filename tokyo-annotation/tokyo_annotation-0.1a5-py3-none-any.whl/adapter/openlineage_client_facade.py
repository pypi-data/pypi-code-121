from typing import Optional
from urllib.parse import urljoin

from openlineage.client import OpenLineageClient, OpenLineageClientOptions

class OpenLineageClientFacade:
    def __init__(
        self,
        openlineageclient: OpenLineageClient = None) -> None:
        self.openlineageclient = openlineageclient
        self.session = openlineageclient.session
    
    @classmethod
    def from_url(
        cls,
        openlineage_url: str,
        openlineage_client_options: Optional[OpenLineageClientOptions] \
                                        = OpenLineageClientOptions()
    ):
        openlineage_client = OpenLineageClient(
                                url=openlineage_url,
                                options=openlineage_client_options)
        
        return cls(openlineage_client)

    @property
    def url(self):
        return self.openlineageclient.url

    @property
    def options(self):
        return self.openlineageclient.options

    def post(self, path, data):
        resp = self.session.post(
            urljoin(self.url, path),
            data,
            timeout=self.options.timeout,
            verify=self.options.verify
        )
        resp.raise_for_status()
        return resp
    
    def get(self, path, params = None):
        resp = self.session.get(
            url=urljoin(self.url, path),
            params=params,
            timeout=self.options.timeout,
            verify=self.options.verify
        )
        resp.raise_for_status()
        return resp