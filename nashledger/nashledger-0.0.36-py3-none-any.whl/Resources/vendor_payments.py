from erp_sync.Resources.resource import Resource

class BillPayments(Resource):

    urls = {}
    
    def set_company_id(self,company_id):
        super().set_company_id(company_id)
        self._set_urls()
        return self

    def _set_urls(self):

        self.urls = {
            "new": f"/companies/{super().get_company_id()}/payments",
            "edit": f"/companies/{super().get_company_id()}/payments",
            "delete": f"/companies/{super().get_company_id()}/payments",
            "import": f"/companies/{super().get_company_id()}/import_payments"
        }

        super().set_urls(self.urls)

        return self
        
    def edit(self,ledger_id = None, payload = None, method='PUT',endpoint=None):
        
        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)
        
        return super().edit(payload, method, endpoint)

    def delete(self, ledger_id=None, payload=None, method='DELETE', endpoint=None):

        self._set_urls()

        payload = {"type": "PurchasePayment"}

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
            "vendor_id": "<Enter vendor id>",
            "reference": "<Enter unique reference>",
            "description": "<Enter description>",
            "date": "<Enter date (yyyy-mm-dd) e.g. 2021-11-22>"
        }

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:

            additional_properties = payload.get("additional_properties", {})

            # If client type is Quickbooks Online
            if super().get_client_type() == super().QBO:            

                data = {"type": "PurchasePayment"}

                if 'type' in additional_properties.keys():
                    data.update({
                        "type": additional_properties.get("type", "PurchasePayment")
                    })

                    additional_properties.pop("type")

                if 'amount' in payload.keys():
                    data.update({
                        "TotalAmt": payload.get("amount", 0)
                    })

                if 'vendor_id' in payload.keys():
                    data.update({
                        "VendorRef": {
                            "value": payload.get("vendor_id", "")
                        }
                    })

                invoices = payload.get("invoice_payments", [])

                for i in range(len(invoices)):
                    invoice = {}
                    if 'amount' in invoices[i].keys():
                        invoice.update({
                            "Amount": invoices[i].get("amount", "")
                        })

                    if 'invoice_id' in invoices[i].keys():
                        invoice.update({
                            "LinkedTxn": [
                                {
                                    "TxnId": invoices[i].get('invoice_id',""),
                                    "TxnType": payload.get("payment_type", "Bill")
                                }
                            ]
                        })
                    
                    invoices[i] = invoice

                # if invoices has data in it
                if bool(invoices):
                    data.update({
                        "Line": invoices
                    })

            # If client type is ZOHO
            elif super().get_client_type() == super().ZOHO:

                data = {"type": "PurchasePayment"}

                if 'type' in additional_properties.keys():
                    data.update({
                        "type": additional_properties.get("type", "PurchasePayment")
                    })

                    additional_properties.pop("type")

                if 'vendor_id' in payload.keys():
                    data.update({
                        "vendor_id": payload.get("vendor_id", "")
                    })

                if 'amount' in payload.keys():
                    data.update({
                        "amount": payload.get("amount", "")
                    })

                if 'reference' in payload.keys():
                    data.update({
                        "reference": payload.get("reference", "")
                    })

                if 'date' in payload.keys():
                    data.update({
                        "date": payload.get("date", "")
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
                        if 'chart_of_account_id' in data[i].keys():
                            data[i]['vendor_id'] = data[i].pop('chart_of_account_id')           
                        if 'reference_number' in data[i].keys():
                            data[i]['reference'] = data[i].pop('reference_number')          
                        if 'total_amount' in data[i].keys():
                            data[i]['amount'] = data[i].pop('total_amount')
                        
            if 'resource' in payload.keys():
                payload["resource"] = data

            super().set_response(payload)

            return self

