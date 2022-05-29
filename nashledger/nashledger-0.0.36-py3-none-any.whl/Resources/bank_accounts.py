from erp_sync.Resources.resource import Resource

class BankAccounts(Resource):

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
            "new" : f"/companies/{super().get_company_id()}/bank_accounts",
            "read" : f"/companies/{super().get_company_id()}/bank_accounts",
            "edit" : f"/companies/{super().get_company_id()}/bank_accounts",
            "delete" : f"/companies/{super().get_company_id()}/bank_accounts",
            "import" : f"/companies/{super().get_company_id()}/import_bank_accounts"
        }

        super().set_urls(self.urls)

        return self
        
    def read(self,bank_account_id = None, payload = None, method='GET',endpoint=None):
        
        self._set_urls()

        if bank_account_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{bank_account_id}'
            super().set_urls(self.urls)
            
        return super().read(payload, method, endpoint)
        
    def edit(self,ledger_id = None, payload = None, method='PUT',endpoint=None):
        
        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)
        
        return super().edit(payload, method, endpoint)
        
    def delete(self,ledger_id = None, payload = None, method='DELETE',endpoint=None):
        
        self._set_urls()

        self.urls["delete"] = f'{self.urls["delete"]}/{ledger_id}'

        super().set_urls(self.urls)
        
        return super().delete(payload, method, endpoint)
        
    def import_data(self,ledger_id = None, payload = None, method='GET',endpoint=None):
        
        self._set_urls()

        if ledger_id is not None:
            self.urls["import"] = f'{self.urls["import"]}/{ledger_id}'

            super().set_urls(self.urls)
            
        return super().import_data(payload, method, endpoint)

    def payload(self):

        data = {
            "account_name": "<Enter a unique name>",
            "account_type": "<Enter account type>",
            "account_number": "<Enter account number>",
            "description": "<Enter account description>"
        }


        # If client type is Quickbooks Online
        if super().get_client_type() ==  super().QBO:

            data.pop("account_number")

        # If client type is XERO
        elif super().get_client_type() == super().XERO:

            data.pop("description")

        return data

    def serialize(self, payload = None, operation = None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"
        
        if operation == super().NEW or operation == super().UPDATE:

            # If client type is Quickbooks Online
            if super().get_client_type() == super().QBO:

                if 'description' in payload.keys():
                    data.update({
                        "Description": payload.get("description", "")
                    })

                if 'account_name' in payload.keys():
                    data.update({
                        "Name": payload.get("account_name", "")
                    })

                if 'account_type' in payload.keys():
                    data.update({
                        "AccountType": payload.get("account_type", "")
                    })

            # If client type is ZOHO
            elif super().get_client_type() == super().ZOHO:

                if 'account_name' in payload.keys():
                    data.update({
                        "account_name": payload.get("account_name", "")
                    })

                if 'account_type' in payload.keys():
                    data.update({
                        "account_type": payload.get("account_type", "")
                    })

                if 'account_number' in payload.keys():
                    data.update({
                        "account_number": payload.get("account_number", "")
                    })

                if 'description' in payload.keys():
                    data.update({
                        "description": payload.get("description", "")
                    })

            # If client type is XERO
            elif super().get_client_type() == super().XERO:

                if 'account_name' in payload.keys():
                    data.update({
                        "Name": payload.get("account_name", "")
                    })

                if 'account_type' in payload.keys():
                    data.update({
                        "Type": payload.get("account_type", "")
                    })

                if 'account_number' in payload.keys():
                    data.update({
                        "BankAccountNumber": payload.get("account_number", "")
                    })

            data.update(payload.get("additional_properties", {}))

            return data

        elif operation == super().READ:

            payload = super().response()

            # confirms if a single object was read from the database
            if isinstance(payload, dict):
                if 'resource' in payload.keys():
                    data = payload.get("resource", []) 

                    # confirms if a single object was read from the database
                    if isinstance(data, dict):
                        data = [data]
                else:
                    data = [payload]

            elif isinstance(payload, list):
                data = payload
            
            if len(data) > 0:
                for i in range(len(data)):
                    if 'name' in data[i].keys():
                        data[i]['account_name'] = data[i].pop('name')

            super().set_response(payload)

            return self