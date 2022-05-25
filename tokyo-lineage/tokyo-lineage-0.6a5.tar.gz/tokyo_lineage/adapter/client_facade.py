from urllib.parse import urljoin

from openlineage.client import OpenLineageClient

class OpenLineageClientFacade:
    def __init__(
        self,
        openlineageclient: OpenLineageClient = None) -> None:
        self.openlineageclient = openlineageclient
        self.session = openlineageclient.session
    
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
            urljoin(self.url, path),
            params,
            timeout=self.options.timeout,
            verify=self.options.verify
        )
        resp.raise_for_status()
        return resp