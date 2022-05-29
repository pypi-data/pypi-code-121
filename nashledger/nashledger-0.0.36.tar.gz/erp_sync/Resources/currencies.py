from erp_sync.Resources.resource import Resource


class Currencies(Resource):

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
            "new": f"/companies/{super().get_company_id()}/currencies",
            "read": f"/companies/{super().get_company_id()}/currencies",
            "edit": f"/companies/{super().get_company_id()}/currencies",
            "delete": f"/companies/{super().get_company_id()}/currencies",
            "import": f"/companies/{super().get_company_id()}/import_currencies"
        }

        super().set_urls(self.urls)

        return self

    def read(self, currency_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if currency_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{currency_id}'
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

        data = {
            "currency_code": "SOS"
        }

        if super().get_client_type() == super().XERO:

            data["additional_properties"] = {
                "help": "Optional fields are placed inside this object",
                "currency_format": "1,234,567.89"
            }

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:

            additional_properties = payload.get("additional_properties", {})

            # If client type is Quickbooks Online or XERO
            if super().get_client_type() == super().QBO or super().get_client_type() == super().XERO:

                if 'currency_code' in payload.keys():
                    data.update({
                        "Code": payload.get("currency_code", "")
                    })

            # If client type is ZOHO
            elif super().get_client_type() == super().ZOHO:

                if 'currency_code' in payload.keys():
                    data.update({
                        "currency_code": payload.get("currency_code", "")
                    })

                data.update({
                    "currency_format": additional_properties.get("AccountCode", "1,234,567.89")
                })

                if 'AccountCode' in additional_properties.keys():
                    additional_properties.pop("AccountCode")

            # If client type is ODOO
            elif super().get_client_type() == super().ODOO:
                if 'currency_code' in payload.keys():
                    data.update({
                        "name": payload.get("currency_code", "")
                    })
                
                if 'currency_name' in payload.keys():
                    data.update({
                        "display_name": payload.get("currency_name", "")
                    })
                
                if 'currency_symbol' in payload.keys():
                    data.update({
                        "symbol": payload.get("currency_symbol", "")
                    })

            data.update(additional_properties)

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

            # No serialization will be done here as the data returned is already in the
            # expected serialized format

            super().set_response(data)

            return self
