from erp_sync.Resources.resource import Resource


class Vendors(Resource):

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
            "new": f"/companies/{super().get_company_id()}/vendors",
            "read": f"/companies/{super().get_company_id()}/vendors",
            "edit": f"/companies/{super().get_company_id()}/vendors",
            "delete": f"/companies/{super().get_company_id()}/vendors",
            "import": f"/companies/{super().get_company_id()}/import_vendors"
        }

        super().set_urls(self.urls)

        return self

    def read(self, vendor_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if vendor_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{vendor_id}'
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
            "name": "Noella Bergstrom CPA",
            "email": "jon@kerluke-tillman.info",
            "city": "Nairobi",
            "phone_number": "2433981830",
            "address": "Flamingo Towers"
        }

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:

            additional_properties = payload.get("additional_properties", {})

            # If client type is Quickbooks Online or MS_DYNAMICS
            if super().get_client_type() == super().MS_DYNAMICS:
                data.update({
                    "name": f'{payload.get("first_name", "")} {payload.get("last_name", "")}',
                    "email": f'{payload.get("email", "")}',
                    "city": f'{payload.get("city", "")}',
                    "phoneNumber": f'{payload.get("phone", "")}',
                    "address": f'{payload.get("address", "")}',
                })
            elif super().get_client_type() == super().QBO:
                data.update({
                    "DisplayName": f'{payload.get("first_name", "")} {payload.get("last_name", "")}',
                    "Title": payload.get("title", ""),
                    "GivenName": payload.get("first_name", ""),
                    "MiddleName": payload.get("last_name", ""),
                    "FamilyName": payload.get("last_name", ""),
                    "PrimaryEmailAddr": {
                        "Address": payload.get("email", "")
                    },
                    "PrimaryPhone": {
                        "FreeFormNumber": payload.get("phone", "")
                    },
                    "type": "Vendor"
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
