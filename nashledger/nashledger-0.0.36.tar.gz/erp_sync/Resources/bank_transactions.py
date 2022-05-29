from erp_sync.Resources.resource import Resource


class BankTransactions(Resource):

    urls = {}

    def set_client_id(self, client_id):
        super().set_client_id(client_id)
        self._set_urls()
        return self

    def set_company_id(self, company_id):
        super().set_company_id(company_id)
        self._set_urls()
        return self

    def _set_urls(self):

        self.urls = {
            "new": f"/companies/{super().get_company_id()}/bank_transactions",
            "read": f"/companies/{super().get_company_id()}/bank_transactions",
            "edit": f"/companies/{super().get_company_id()}/bank_transactions",
            "delete": f"/companies/{super().get_company_id()}/bank_transactions",
            "import" : f"/companies/{super().get_company_id()}/import_bank_transactions"
        }

        super().set_urls(self.urls)

        return self

    def read(self, bank_transaction_id=None, payload=None, method='GET', endpoint=None):
        
        self._set_urls()

        if bank_transaction_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{bank_transaction_id}'
            super().set_urls(self.urls)

        return super().read(payload, method, endpoint)

    def edit(self, ledger_id=None, payload=None, method='PUT', endpoint=None):
        
        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().edit(payload, method, endpoint)

    def delete(self, ledger_id=None, payload=None, method='DELETE', endpoint=None):
        
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
            "from_account_id": "<Enter from account id>",
            "to_account_id": "<Enter to account id>",
            "transaction_type": "<Enter transaction type>",
            "amount": "<Enter amount>",
            "payment_mode": "<Enter payment mode>",
            "date": "<Enter date - yyyy-mm-dd> e.g. 2021-07-06",
            "reference": "<Enter unique reference>"
        }

        # If client type is XERO
        if super().get_client_type() == super().XERO:
            data["to_account_id"] = f'{data["to_account_id"]} i.e. Chart of Account ID'

        return data

    def serialize(self, payload = None, operation = None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"
        
        if operation == super().NEW or operation == super().UPDATE:

            additional_properties = payload.get("additional_properties", {})

            # If client type is Quickbooks Online or ZOHO
            if super().get_client_type() == super().QBO or super().get_client_type() == super().ZOHO:

                # since the standardized payload is the actual payload expected by QBO and ZOHO
                # there is no need to serialize much of the payload
                data = payload
                if 'reference' in payload.keys():
                    data['reference_number'] = data.pop('reference')

            # since the standardized payload is the actual payload expected by QBO and ZOHO
            # we are only going to serialize XERO

            # If client type is Quickbooks Online
            elif super().get_client_type() == super().XERO:

                bank_transactions = {}

                if 'transaction_type' in payload.keys():
                    bank_transactions.update({
                        "Type": payload.get("transaction_type", "")
                    })

                if 'reference' in payload.keys():
                    bank_transactions.update({
                        "Reference": payload.get("reference", "")
                    })

                if 'from_account_id' in payload.keys():
                    bank_transactions.update({
                        "Contact": {
                                "ContactID": payload.get("from_account_id", "")
                            }
                    })

                if 'amount' in payload.keys():
                    bank_transactions.update({
                        "Lineitems": [
                                {
                                    # set to 1 by default
                                    "Quantity": additional_properties.get("Quantity", 1),
                                    "UnitAmount": payload.get("amount", 0),
                                    # set to “400” by default
                                    "AccountCode": additional_properties.get("AccountCode", "400")
                                }
                            ]
                    })

                if 'Quantity' in additional_properties.keys():
                    additional_properties.pop("Quantity")

                if 'AccountCode' in additional_properties.keys():
                    additional_properties.pop("AccountCode")

                if 'to_account_id' in payload.keys():
                    bank_transactions.update({
                        "BankAccount": {
                                "AccountID": payload.get("to_account_id", "")
                            }
                    })
                
                data.update({
                    "BankTransactions": [bank_transactions]
                })

            data.update(additional_properties)

            return data

        elif operation == super().READ:

            payload = super().response()

            data = payload

            # confirms if a single object was read from the database
            if isinstance(payload, dict):
                if 'resource' in payload.keys():
                    data = payload.get("resource", [])
                
            # confirms if a single object was read from the database
            if isinstance(data, dict):
                data = [data]
            
            # confirms if data is a list
            if isinstance(data, list):
                if len(data) > 0:
                    for i in range(len(data)):
                        if 'unit_price' in data[i].keys():
                            data[i]['value'] = data[i].pop('unit_price')
                        
            if isinstance(payload, dict):
                if 'resource' in payload.keys():
                    payload["resource"] = data
            else:
                payload = data

            super().set_response(payload)

            return self