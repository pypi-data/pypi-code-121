from erp_sync.Resources.resource import Resource


class Items(Resource):

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
            "new": f"/companies/{super().get_company_id()}/items",
            "edit": f"/companies/{super().get_company_id()}/items",
            "read": f"/companies/{super().get_company_id()}/items",
            "delete": f"/companies/{super().get_company_id()}/items",
            "import": f"/companies/{super().get_company_id()}/import_items"
        }

        super().set_urls(self.urls)

        return self

    def read(self, item_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if item_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{item_id}'
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

    def import_data(self, ledger_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if ledger_id is not None:
            self.urls["import"] = f'{self.urls["import"]}/{ledger_id}'
            super().set_urls(self.urls)

        return super().import_data(payload, method, endpoint)

    def payload(self):

        data = {}

        # If client type is Quickbooks Online
        if super().get_client_type() == super().QBO:

            data = {
                "type": "<Enter type either purchase or sales>",
                "name": "<Enter a unique name>",
                "value": "<Enter the item value>"
            }

        # If client type is ZOHO
        elif super().get_client_type() == super().ZOHO:

            data = {
                "description": "<Enter item description>",
                "name": "<Enter item name>",
                "item_code": "<Enter item item_code, ZOHO refers to this as the item_code>"
            }

        # If client type is XERO
        elif super().get_client_type() == super().XERO:

            data = {
                "Items": [
                    {
                        "Code": "<Enter item item_code, XERO refers to this as the Code>",
                        "Name": "<Enter item name>",
                        "Description": "<Enter item description>",
                        "TotalCostPool": "<Enter the item value>"
                    }
                ]
            }

        data.update({
            "additional_properties": {
                "help": "Optional data are passed inside this object, the format should be specific to the ERP. View ERP documentation for more details, below are examples of optional data",
            }
        })

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:

            # If client type is Quickbooks Online
            if super().get_client_type() == super().QBO:

                if 'name' in payload.keys():
                    data.update({
                        "Name": payload.get("name", "")
                    })

                if 'value' in payload.keys():
                    data.update({
                        "UnitPrice": payload.get("value", 0)
                    })
                
                data.update({
                    "Type": payload.get("type", "")
                })

                if payload.get("type", "") == "Inventory":
                    data.update({
                        "QtyOnHand": payload.get("qty_on_hand", 0),
                        "TrackQtyOnHand": payload.get("track_qty_on_hand", True)
                    })

            # If client type is ZOHO
            elif super().get_client_type() == super().ZOHO:

                if 'description' in payload.keys():
                    data.update({
                        "description": payload.get("description", "")
                    })

                if 'name' in payload.keys():
                    data.update({
                        "name": payload.get("name", "")
                    })

                if 'item_code' in payload.keys():
                    data.update({
                        "sku": payload.get("item_code", "")
                    })

            # If client type is XERO
            elif super().get_client_type() == super().XERO:

                items = {}

                if 'item_code' in payload.keys():
                    items.update({
                        "Code": payload.get("item_code", "")
                    })

                if 'name' in payload.keys():
                    items.update({
                        "Name": payload.get("name", "")
                    })

                if 'description' in payload.keys():
                    items.update({
                        "Description": payload.get("description", "")
                    })

                if 'item_code' in payload.keys():
                    items.update({
                        "TotalCostPool": payload.get("value", "")
                    })

                # If items has data
                if bool(items):
                    data["Items"] = [items]

            # If client type is ODOO
            elif super().get_client_type() == super().ODOO:
                data = {
                    "name": payload.get("name", ""),
                    "display_name": payload.get("name", ""),
                    "description": payload.get("description", ""),
                    "price": payload.get("value", 0)
                }

            # If client type is MS_DYNAMICS
            elif super().get_client_type() == super().MS_DYNAMICS:
                data.update({
                    "description": f'{payload.get("description", "")}',
                    "baseUnitOfMeasure": f'{payload.get("base_unit_of_measure", "")}',
                    "unitPrice": payload.get("unit_price", 0),
                })

            data.update(payload.get("additional_properties", {}))

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
