from erp_sync.Resources.resource import Resource

class Records(Resource):

    urls = {}

    def set_client_id(self, client_id):
        super().set_client_id(client_id)
        self._set_urls()
        return self
    
    def set_company_id(self,company_id):
        super().set_company_id(company_id)
        self._set_urls()
        return self

    def _set_urls(self):

        self.urls = {
            "read" : f"/clients/{super().get_client_id()}",
        }

        super().set_urls(self.urls)

        return self
        
    def read(self,record_id = None, payload = None, method='GET',endpoint="/records"):

        endpoint = self.urls["read"] + endpoint

        if record_id is not None:
            endpoint = f'{endpoint}/{record_id}'
        
        return super().read(payload, method, endpoint)

    def sync_record_to_erp(self,record_id = None, payload = None, method='POST',endpoint="/sync_record"):

        return super().read(payload, method, endpoint = f'/companies/{super().get_company_id()}/records/{record_id}{endpoint}') 
    
    def account_number_recon(self,record_id = None, payload = None, method='POST',endpoint="/account_number_recon"):

        return super().read(payload, method, endpoint = f'/companies/{super().get_company_id()}/records/{record_id}{endpoint}') 
    
    def new_invoice_recon(self,record_id = None, payload = None, method='POST',endpoint="/new_invoice_recon"):

        return super().read(payload, method, endpoint = f'/companies/{super().get_company_id()}/records/{record_id}{endpoint}') 

    