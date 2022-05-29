from erp_sync.Resources.resource import Resource
import os

class Uploads(Resource):

    urls = {}

    def set_company_id(self, company_id):
        super().set_company_id(company_id)
        self._set_urls()
        return self

    def _set_urls(self):

        self.urls = {
            "new": f"/clients/{super().get_client_id()}/uploads",
            "read": f"/clients/{super().get_client_id()}/uploads",
            "edit": f"/clients/{super().get_client_id()}/uploads",
        }

        super().set_urls(self.urls)

        return self

    def new(self, file_name="", path="path", payload=None, method='POST'):

        file_type = ""

        if 'file_type' in payload.keys():
            file_type = payload.get("file_type", "")
            
            payload.pop("file_type")

        files = [
            ('file', (file_name, open(
                path, 'rb'), file_type))
        ]

        return super().new(payload, method, endpoint = self.urls["new"], files = files)

    def read(self, upload_id=None, payload=None, method='GET', endpoint=None):

        if upload_id is not None:
            endpoint = f'{self.urls["read"]}/{upload_id}'

        return super().read(payload, method, endpoint)

    def edit(self, upload_id=None, file_name="", path="path", payload=None, method='PUT'):

        file_type = ""

        if 'file_type' in payload.keys():
            file_type = payload.get("file_type", "")
            
            payload.pop("file_type")

        files = [
            ('file', (file_name, open(
                path, 'rb'), file_type))
        ]

        return super().edit(payload, method, endpoint = f'{self.urls["edit"]}/{upload_id}', files = files)

    def create_bank_account(self, upload_id=None, payload=None, method='POST', endpoint="/bank_account"):

        endpoint = f"/clients/{super().get_client_id()}/companies/{super().get_company_id()}/uploads/{upload_id}{endpoint}"

        return super().new(payload, method, endpoint=endpoint)

    def create_bank_transaction(self, upload_id=None, payload=None, method='POST', endpoint="/bank_transactions"):

        endpoint = f"/clients/{super().get_client_id()}/companies/{super().get_company_id()}/uploads/{upload_id}{endpoint}"

        return super().new(payload, method, endpoint=endpoint)

    def get_uploaded_records(self, upload_id=None, record_id=None, payload=None, method='GET', endpoint=None):

        endpoint = f'{self.urls["read"]}/{upload_id}/records'

        if record_id is not None:
            endpoint += f'/{record_id}'

        return super().read(payload, method, endpoint=endpoint)
