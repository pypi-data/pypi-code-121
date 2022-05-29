from erp_sync.Resources.resource import Resource

class BillInvoices(Resource):

    urls = {}

    def set_company_id(self, company_id):
        super().set_company_id(company_id)
        self._set_urls()
        return self

    def _set_urls(self):

        self.urls = {
            "new": f"/companies/{super().get_company_id()}/invoices",
            "edit": f"/companies/{super().get_company_id()}/invoices",
            "import": f"/companies/{super().get_company_id()}/import_bills",
        }

        super().set_urls(self.urls)

        return self

    def edit(self, ledger_id=None, payload=None, method='PUT', endpoint=None):

        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().edit(payload, method, endpoint)

    def import_data(self, ledger_id=None, payload=None, method='GET', endpoint=None):
        
        self._set_urls()

        if ledger_id is not None:
            self.urls["import"] = f'{self.urls["import"]}/{ledger_id}'
            super().set_urls(self.urls)

        return super().import_data(payload, method, endpoint)

    def payload(self):

        data = {
            "vendor_id ": "<Enter vendor id>",
            "item_id": "<Enter item id>",
            "amount": "<Enter amount",

            "additional_properties":{
                "help":"Optional or extra parameters go here",
                "bill_number": "<Enter the unique bill number or the system will automatically generate one for you>",
            }
        }

        return data


    def serialize(self, payload = None, operation = None):

        data = {"type": "PurchaseInvoice"}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"
        
        if operation == super().NEW or operation == super().UPDATE:

            additional_properties = payload.get("additional_properties", {})        

            # If client type is ZOHO
            if super().get_client_type() == super().ZOHO:

                if 'vendor_id' in payload.keys():
                    data.update({
                        "vendor_id": payload.get("vendor_id", "")
                    })

                if 'vendor_invoice_no' in payload.keys():
                    data.update({
                        "bill_number": payload.get("vendor_invoice_no", super().generate_code())
                    })

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    if "item_ledger_id" in line_items[i].keys():
                        line_items[i]["item_id"] = line_items[i].pop("item_ledger_id")
                    if "price" in line_items[i].keys():
                        line_items[i]["rate"] = line_items[i].pop("price")
                    if "quantity" in line_items[i].keys():
                        line_items[i]["quantity"] = line_items[i].pop("quantity")

                    if 'type' in line_items[i].keys():
                        line_items[i].pop("type")
                    if 'unit_of_measure' in line_items[i].keys():
                        line_items[i].pop("unit_of_measure")
                    if 'amount' in line_items[i].keys():
                        line_items[i].pop("amount")
                    if 'chart_of_account' in line_items[i].keys():
                        line_items[i].pop("chart_of_account")
                
                if 'item_id' in payload.keys():
                    payload.pop("item_id") 
                if 'currency_code' in payload.keys():
                    payload.pop("currency_code")  
                if 'amount' in payload.keys():
                    payload.pop("amount")               

                # if line_items has data in it
                if bool(line_items):
                    data.update({
                        "line_items": [line_items]
                    })

            # If client type is Quickbooks Online
            elif super().get_client_type() == super().QBO:

                if 'vendor_id' in payload.keys():
                    data.update({
                        "VendorRef": {
                            "value": payload.get("vendor_id", 0)
                        }
                    })
                
                if "currency_code" in payload.keys():
                    data.update({
                        "CurrencyRef": {
                            "value": payload.get("currency_code", "KES")
                        }
                    })

                line_items = {}

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    line_items[i]["DetailType"] = "AccountBasedExpenseLineDetail"
                    line_items[i]["AccountBasedExpenseLineDetail"] = {
                        "AccountRef": {
                            "value": line_items[i].pop("chart_of_account")
                        }
                    }
                    line_items[i]["Amount"] = line_items[i].pop("amount")

                # if line_items has data in it
                if bool(line_items):
                    data.update({
                        "Line": [line_items]
                    })

            # If client type is MS_DYNAMICS
            elif super().get_client_type() == super().MS_DYNAMICS:
                data.update({
                    "vendor_number": f'{payload.get("vendor_id", "")}',
                    "vendor_invoice_no": f'{payload.get("vendor_invoice_no", "")}',
                })

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    if "item_ledger_id" in line_items[i].keys():
                        line_items[i]["item_id"] = line_items[i].pop(
                            "item_ledger_id"
                        )
                    if "quantity" in line_items[i].keys():
                        line_items[i]["quantity"] = line_items[i].pop("quantity")
                    if "price" in line_items[i].keys():
                        line_items[i]["unit_price"] = line_items[i].pop("price")
                    if "type" in line_items[i].keys():
                        line_items[i]["type"] = line_items[i].pop("type")
                    if "unit_of_measure" in line_items[i].keys():
                        line_items[i]["unit_of_measure"] = line_items[i].pop("unit_of_measure")

                # if line_items has data in it
                if bool(line_items):
                    data.update({"create_vendor_invoice_details": line_items})

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
                        if 'total_amount' in data[i].keys():
                            data[i]['amount'] = data[i].pop('total_amount')
                        if 'customer_id' in data[i].keys():
                            data[i]['vendor_id'] = data[i].pop('customer_id')
                        
            if 'resource' in payload.keys():
                payload["resource"] = data

            super().set_response(payload)

            return self