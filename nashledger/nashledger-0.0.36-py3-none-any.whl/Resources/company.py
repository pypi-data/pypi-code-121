from erp_sync.Resources.resource import Resource

class Company(Resource):

    urls = {}

    def _set_urls(self):

        self.urls = {
            "read" : f"/companies",
        }

        super().set_urls(self.urls)

        return self
        
    def read(self,company_id = None, payload = None, method='GET',endpoint=None):
        
        self._set_urls()

        if company_id is not None:
            endpoint = f'{self.urls["read"]}/{company_id}'
        
        return super().read(payload, method, endpoint)