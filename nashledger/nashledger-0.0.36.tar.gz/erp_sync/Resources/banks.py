from erp_sync.Resources.resource import Resource


class Banks(Resource):

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
            "new": f"/companies/{super().get_company_id()}/banks",
            "edit": f"/companies/{super().get_company_id()}/banks",
            "read": f"/companies/{super().get_company_id()}/banks",
            "delete": f"/companies/{super().get_company_id()}/banks",
            "import": f"/companies/{super().get_company_id()}/import_banks"
        }

        super().set_urls(self.urls)

        return self

    def read(self, bank_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if bank_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{bank_id}'
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
        if super().get_client_type() == super().ODOO:

            data = {
                "name": "Test Bank"
            }

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:

            # If client type is ODOO
            if super().get_client_type() == super().ODOO:

                if 'name' in payload.keys():
                    data.update({
                        "name": payload.get("name", "")
                    })

            data.update(payload.get("additional_properties", {}))

            return data

        elif operation == super().READ:

            super().set_response(payload)

            return self
