class InternetData(object):

    def __init__(
        self, order_id, phone_number, iban, email, service_address, service_city, service_zip,
        service_subdivision, service_subdivision_code, shipment_address, shipment_city, shipment_zip,
        shipment_subdivision, previous_service, previous_provider, previous_internal_provider,
        previous_owner_vat, previous_owner_name, previous_owner_surname, notes, product,
            adsl_coverage, mm_fiber_coverage, vdf_fiber_coverage, orange_fiber_coverage, type,
            previous_contract_address="", previous_contract_phone=""):

        # Common all the Tickets
        self.order_id = order_id
        self.phone_number = phone_number
        self.iban = iban
        self.email = email
        self.previous_provider = previous_provider
        self.previous_internal_provider = previous_internal_provider
        self.previous_owner_vat = previous_owner_vat
        self.previous_owner_name = previous_owner_name
        self.previous_owner_surname = previous_owner_surname
        self.product = product

        # Common Internet the Tickets
        self.service_address = service_address
        self.service_city = service_city
        self.service_zip = service_zip
        self.service_subdivision = service_subdivision
        self.service_subdivision_code = service_subdivision_code
        self.shipment_address = shipment_address
        self.shipment_city = shipment_city
        self.shipment_zip = shipment_zip
        self.shipment_subdivision = shipment_subdivision
        self.previous_service = previous_service
        self.notes = notes
        self.adsl_coverage = adsl_coverage
        self.mm_fiber_coverage = mm_fiber_coverage
        self.vdf_fiber_coverage = vdf_fiber_coverage
        self.orange_fiber_coverage = orange_fiber_coverage
        self.type = type
        self.previous_contract_address = previous_contract_address
        self.previous_contract_phone = previous_contract_phone
