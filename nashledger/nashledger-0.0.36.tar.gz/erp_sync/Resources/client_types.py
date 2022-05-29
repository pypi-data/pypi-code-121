from erp_sync.Resources.resource import Resource

class ClientTypes(Resource):

    urls = {}

    def _set_urls(self):

        self.urls = {
            "new" : f"/client_types",
            "read" : f"/client_types"
        }

        super().set_urls(self.urls)

        return self
        
    def read(self,client_type_id = None, payload = None, method='GET',endpoint=None):
        
        self._set_urls()

        if client_type_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{client_type_id}'
            super().set_urls(self.urls)
        
        return super().read(payload, method, endpoint)