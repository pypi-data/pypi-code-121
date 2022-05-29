from erp_sync.Resources.resource import Resource

class BankTransfers(Resource):

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
            "new" : f"/companies/{super().get_company_id()}/bank_transfers",
            "edit" : f"/companies/{super().get_company_id()}/bank_transfers",
            "read" : f"/companies/{super().get_company_id()}/bank_transfers",
            "delete" : f"/companies/{super().get_company_id()}/bank_transfers",
            "import" : f"/companies/{super().get_company_id()}/import_bank_transfers"
        }

        super().set_urls(self.urls)

        return self
        
    def read(self,bank_transfer_id = None, payload = None, method='GET',endpoint=None):
        
        self._set_urls()

        if bank_transfer_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{bank_transfer_id}'
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
                "amount": "<Enter amount>",
                "to_account_id": "<Enter to account id>",
                "from_account_id": "<Enter from account id>",
                "reference": "<Enter reference>"
            }

        return data

    
    def serialize(self, payload = None, operation = None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"
        
        if operation == super().NEW or operation == super().UPDATE:

            # If client type is Quickbooks Online
            if super().get_client_type() == super().QBO:

                if 'amount' in payload.keys():
                    data.update({
                        "Amount": payload.get("amount", "")
                    })

                if 'to_account_id' in payload.keys():
                    data.update({
                        "ToAccountRef": {
                            "value": payload.get("to_account_id", "")
                        }
                    })

                if 'from_account_id' in payload.keys():
                    data.update({
                        "FromAccountRef": {
                            "value": payload.get("from_account_id", "")
                        }
                    })

                if 'reference' in payload.keys():
                    data.update({
                        "PrivateNote": payload.get("reference", "")
                    })

            # If client type is XERO
            elif super().get_client_type() == super().XERO:

                bank_transfers = {}

                if 'from_account_id' in payload.keys():
                    bank_transfers.update({
                        "FromBankAccount": {
                            "AccountID": payload.get("from_account_id", "")
                        }
                    })

                if 'to_account_id' in payload.keys():
                    bank_transfers.update({
                        "ToBankAccount": {
                            "AccountID": payload.get("to_account_id", "")
                        }
                    })

                if 'amount' in payload.keys():
                    bank_transfers.update({
                        "Amount": payload.get("amount", "")
                    })

                if 'reference' in payload.keys():
                    bank_transfers.update({
                        "Reference": payload.get("reference", "")
                    })
                
                # If bank_transfers has data
                if bool(bank_transfers):
                    data["BankTransfers"] = [bank_transfers]

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

            super().set_response(payload)

            return self
