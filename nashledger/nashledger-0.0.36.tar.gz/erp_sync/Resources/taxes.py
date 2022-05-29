from erp_sync.Resources.resource import Resource


class Taxes(Resource):

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
            "new": f"/companies/{super().get_company_id()}/taxes",
            "read": f"/companies/{super().get_company_id()}/taxes",
            "edit": f"/companies/{super().get_company_id()}/taxes",
            "delete": f"/companies/{super().get_company_id()}/taxes",
            "import": f"/companies/{super().get_company_id()}/import_taxes"
        }

        super().set_urls(self.urls)

        return self

    def read(self, tax_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if tax_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{tax_id}'

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

    def tax_agency_create(self, payload=None, method='POST', endpoint=None):

        endpoint = f"/companies/{super().get_company_id()}/tax_agencies"

        return super().new(payload, method, endpoint)

    def tax_agency_get(self, tax_agency_id=None, payload=None, method='GET', endpoint=None):

        endpoint = f"/companies/{super().get_company_id()}/tax_agencies"

        if tax_agency_id is not None:
            endpoint = f'{endpoint}/{tax_agency_id}'

        return super().read(payload, method, endpoint)

    def payload(self):

        data = {
            "name": "<Enter unique tax name>",
            "rate": "<Enter tax rate>",
            "type": "<Enter tax type>"
        }

        if super().get_client_type() == super().QBO:

            data.update({
                "additional_properties": {
                    "help": "The TaxAgencyId below is only applicable in quickbooks. Visit their documentation for more details",
                    "TaxAgencyId": "Enter tax agency id. Get it by calling tax agency api to get a list of tax agencies, or create a tax agency"
                }
            })

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:
            
            additional_properties = payload.get("additional_properties", {})

            # If client type is ZOHO
            if super().get_client_type() == super().ZOHO:

                if 'name' in payload.keys():
                    data.update({
                        "tax_name": payload.get("name", "")
                    })

                if 'rate' in payload.keys():
                    data.update({
                        "tax_percentage": payload.get("rate", "")
                    })

                if 'type' in payload.keys():
                    data.update({
                        "tax_type": payload.get("type", "")
                    })

            # If client type is XERO
            elif super().get_client_type() == super().XERO:

                tax_rates = {}

                tax_components = {}

                if 'rate' in payload.keys():
                    data.update({
                        "tax_percentage": payload.get("rate", "")
                    })

                    tax_components.update({
                        "Rate": payload.get("rate", "")
                    })

                if 'type' in payload.keys():
                    tax_components.update({
                        "Name": payload.get("type", "")
                    })

                # if tax_components has data in it
                if bool(tax_components):
                    tax_rates.update({
                        "TaxComponents": [tax_components]
                    })

                if 'name' in payload.keys():
                    tax_rates.update({
                        "Name": payload.get("name", "")
                    })

                # if tax_components has data in it
                if bool(tax_rates):
                    data.update({
                        "TaxRates": [tax_rates]
                    })

            # If client type is Quickbooks Online
            elif super().get_client_type() == super().QBO:

                tax_rate_details = {}

                if 'rate' in payload.keys():
                    tax_rate_details.update({
                        "RateValue": payload.get("rate", "")
                    })

                if 'name' in payload.keys():
                    tax_rate_details.update({
                        "TaxRateName": payload.get("name", "")
                    })

                if 'TaxAgencyId' in additional_properties.keys():
                    tax_rate_details.update({
                        "TaxAgencyId": f'{additional_properties.get("TaxAgencyId", 0)}'
                    })

                    additional_properties.pop("TaxAgencyId")

                if bool(tax_rate_details):

                    data.update({
                        "TaxRateDetails": [tax_rate_details]
                    })

                if 'type' in payload.keys():
                    data.update({
                        "TaxCode": payload.get("type", "")
                    })

            # If client type is ODOO
            elif super().get_client_type() == super().ODOO:
                data = {
                    "active":True
                }
                if 'name' in payload.keys():
                    data.update({
                        "name": payload.get("name", "")
                    })
                if 'type' in payload.keys():
                    data.update({
                        "amount_type": payload.get("type", "")
                    })
                if 'rate' in payload.keys():
                    data.update({
                        "amount": payload.get("rate", "")
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
                        if 'tax_percentage' in data[i].keys():
                            data[i]['rate'] = data[i].pop('tax_percentage')
                        if 'tax_type' in data[i].keys():
                            data[i]['type'] = data[i].pop('tax_type')
                        
            if isinstance(payload, dict):
                if 'resource' in payload.keys():
                    payload["resource"] = data
            else:
                payload = data

            super().set_response(payload)

            return self