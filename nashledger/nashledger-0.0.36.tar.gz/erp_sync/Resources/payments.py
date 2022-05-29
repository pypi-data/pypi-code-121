from erp_sync.Resources.resource import Resource


class Payments(Resource):

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
            "new": f"/companies/{super().get_company_id()}/payments",
            "edit": f"/companies/{super().get_company_id()}/payments",
            "delete": f"/companies/{super().get_company_id()}/payments",
            "read": f"/companies/{super().get_company_id()}/payments",
            "import": f"/companies/{super().get_company_id()}/import_payments"
        }

        super().set_urls(self.urls)

        return self

    def read(self, payment_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if payment_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{payment_id}'
            super().set_urls(self.urls)

        return super().read(payload, method, endpoint)

    def edit(self, ledger_id=None, payload=None, method='PUT', endpoint=None):

        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().edit(payload, method, endpoint)

    def delete(self, ledger_id=None, payload=None, method='DELETE', endpoint=None):

        payload = {"type": "SalesPayment"}

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
            "amount": "<Enter amount>",
            "customer_id": "<Enter customer id>",
            "reference": "<Enter unique reference>",
            "description": "<Enter description>",
            "date": "<Enter date (yyyy-mm-dd) e.g. 2021-11-22>"
        }

        # If client type is ZOHO
        if super().get_client_type() == super().XERO:
            data["customer_id"] = "<Chart of Account ID>"
            data["invoice_id"] = "<Enter invoice id>"

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:

            data["type"] = "SalesPayment"

            if 'type' in payload.keys():
                data["type"] = payload.get("type", "SalesPayment")

            additional_properties = payload.get("additional_properties", {})

            # If client type is Quickbooks Online
            if super().get_client_type() == super().QBO:

                if 'amount' in payload.keys():
                    data.update({
                        "TotalAmt": payload.get("amount", "")
                    })

                if 'customer_id' in payload.keys():
                    data.update({
                        "CustomerRef": {
                            "value": payload.get("customer_id", "")
                        }
                    })

                if 'currency_code' in payload.keys():
                    data.update({
                        "CurrencyRef": {
                            "value": payload.get("currency_code", "KES")
                        }
                    })

                if 'account_id' in payload.keys():
                    data.update({
                        "DepositToAccountRef": {
                            "value": payload.get("account_id", "")
                        }
                    })

                if 'reference' in payload.keys():
                    data.update({
                        "PaymentRefNum": payload.get("reference", "")
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
                                    "TxnType": "Invoice"
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

                payment = {}

                if 'customer_id' in payload.keys():
                    payment.update({
                        "customer_id": payload.get("customer_id", "")
                    })

                if 'amount' in payload.keys():
                    payment.update({
                        "amount": payload.get("amount", "")
                    })

                if 'reference' in payload.keys():
                    payment.update({
                        "reference": payload.get("reference", "")
                    })

                if 'description' in payload.keys():
                    payment.update({
                        "description": payload.get("description", "")
                    })

                if 'date' in payload.keys():
                    payment.update({
                        "date": payload.get("date", "")
                    })

                invoices = payload.get("invoice_payments", [])

                for i in range(len(invoices)):
                    if 'invoice_id' in invoices[i].keys():
                        invoices[i]['invoice_id'] = invoices[i].pop(
                            'invoice_id')
                    if 'amount' in invoices[i].keys():
                        invoices[i]['amount_applied'] = invoices[i].pop(
                            'amount')
                    
                    invoices[i].pop('payment_date')
                    invoices[i].pop('payment_reference')
                    invoices[i].pop('payment_type')
                    invoices[i].pop('account_id')
                # if invoices has data in it
                if bool(invoices):
                    payment.update({
                        "invoices": invoices
                    })

                if bool(payment):
                    data.update({
                        "payment": payment
                    })

            # If client type is SAP
            elif super().get_client_type() == super().SAP:
                header = {}

                header.update({
                    "Type": data.get("type", "")
                })

                if 'date' in payload.keys():
                    header.update({
                        "DocDate": payload.get("date", "")
                    })

                if 'customer_id' in payload.keys():
                    header.update({
                        "CardCode": payload.get("customer_id", "")
                    })

                if 'invoice_id' in payload.keys():
                    header.update({
                        "InvoiceDocEntry": payload.get("invoice_id", "")
                    })
                
                if 'SourceNumber' in additional_properties.keys():
                    header.update({
                        "SourceNumber": additional_properties.get("SourceNumber", "")
                    })
                    
                    additional_properties.pop("SourceNumber")
                
                if 'PostingDate' in additional_properties.keys():
                    header.update({
                        "PostingDate": additional_properties.get("PostingDate", "")
                    })
                    
                    additional_properties.pop("PostingDate")
                
                if 'DocCurrency' in additional_properties.keys():
                    header.update({
                        "DocCurrency": additional_properties.get("DocCurrency", "")
                    })
                    
                    additional_properties.pop("DocCurrency")
                
                if 'CardType' in additional_properties.keys():
                    header.update({
                        "CardType": additional_properties.get("CardType", "")
                    })
                    
                    additional_properties.pop("CardType")
                
                if 'ReceiptNo' in additional_properties.keys():
                    header.update({
                        "ReceiptNo": additional_properties.get("ReceiptNo", "")
                    })
                    
                    additional_properties.pop("ReceiptNo")
                
                invoice_payments = payload.get("invoice_payments", [])

                for i in range(len(invoice_payments)):
                    invoice_payments[i].pop('invoice_id')
                    if 'payment_date' in invoice_payments[i].keys():
                        invoice_payments[i]['PaymentDate'] = invoice_payments[i].pop(
                            'payment_date')
                    if 'payment_reference' in invoice_payments[i].keys():
                        invoice_payments[i]['PaymentReference'] = invoice_payments[i].pop(
                            'payment_reference')
                    if 'payment_type' in invoice_payments[i].keys():
                        invoice_payments[i]['PaymentType'] = invoice_payments[i].pop(
                            'payment_type')
                    if 'account_id' in invoice_payments[i].keys():
                        invoice_payments[i]['Account'] = invoice_payments[i].pop(
                            'account_id')
                    if 'amount' in invoice_payments[i].keys():
                        invoice_payments[i]['Amount'] = invoice_payments[i].pop(
                            'amount')

                # if invoice_payments has data in it
                if bool(invoice_payments):
                    header.update({
                        "Payments": invoice_payments
                    })
                
                # if header has data in it
                if bool(header):
                    data.update({
                        "Header": header
                    })

            # If client type is ZOHO
            elif super().get_client_type() == super().XERO:

                data = {}

                payment = {}

                if 'date' in payload.keys():
                    payment.update({
                        "Date": payload.get("date", "")
                    })

                if 'amount' in payload.keys():
                    payment.update({
                        "Amount": payload.get("amount", "")
                    })

                if 'reference' in payload.keys():
                    payment.update({
                        "Reference": payload.get("reference", "")
                    })

                if 'account_id' in payload.keys():
                    payment.update({
                        "Account": {
                            "AccountID": payload.get("account_id", "")
                        }
                    })

                if 'invoice_id' in payload.keys():
                    payment.update({
                        "Invoice": {
                            "InvoiceID": payload.get("invoice_id", ""),
                            "LineItems": payload.get("invoice_payments", []),
                        }
                    })

                if bool(payment):
                    data.update({
                        "Payments": [payment]
                    })

            # If client type is ODOO
            elif super().get_client_type() == super().ODOO:
                data = {
                    "partner_type": "customer",
                    "date": payload.get("date", ""),
                    "amount": payload.get("amount", 0),
                    "partner_id": payload.get("customer_id", ""),
                    "payment_reference": payload.get("reference", ""),
                }

            # If client type is MS_DYNAMICS
            elif super().get_client_type() == super().MS_DYNAMICS:
                data.update({
                    "paymentReference": payload.get("reference", ""),
                    "ownerInvoiceType": "Customer",
                    "ownerInvoiceNumber": f'{payload.get("invoice_id", "")}',
                    "ownerNumber": payload.get("customer_id", ""),
                    "description": payload.get("description", ""),
                    "amount": f'{payload.get("amount", "")}',
                    "bankCode": payload.get("bank_code", ""),
                })

            data.update(additional_properties)

            return data

        elif operation == super().READ:

            payload = super().response()

            if 'data' in payload.keys():
                payload = payload.get("data", [])

            elif 'resource' in payload.keys():
                payload = payload.get("resource", [])

            # confirms if a single object was read from the database
            if isinstance(payload, dict):
                payload = [payload]

            if payload is not None:
                
                if len(payload) > 0:
                    for i in range(len(payload)):
                        if 'chart_of_account_id' in payload[i].keys():
                            payload[i]['customer_id'] = payload[i].pop(
                                'chart_of_account_id')
                        if 'reference_number' in payload[i].keys():
                            payload[i]['reference'] = payload[i].pop(
                                'reference_number')
                        if 'total_amount' in payload[i].keys():
                            payload[i]['amount'] = payload[i].pop('total_amount')
                
            else:
                payload = super().response()

            super().set_response(payload)

            return self
