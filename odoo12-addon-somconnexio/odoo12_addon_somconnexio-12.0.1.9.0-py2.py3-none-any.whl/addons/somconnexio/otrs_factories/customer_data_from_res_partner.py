from otrs_somconnexio.otrs_models.customer_data import CustomerData


class CustomerDataFromResPartner:

    def __init__(self, partner):
        self.partner = partner

    def build(self):
        customer_params = {
            "id": self.partner.ref,
            "vat_number": self.partner.vat,
            "first_name": self.partner.firstname,
            "name": self.partner.lastname,
            "phone": self.partner.mobile or self.partner.phone,
            "street": self.partner.full_street,
            "zip": self.partner.zip,
            "city": self.partner.city,
            "subdivision": "{}-{}".format(
                self.partner.country_id.code,
                self.partner.state_id.code
            ),
        }
        if self.partner.is_company:
            customer_params.update({
                "first_name": self.partner.lastname,
                "name": ""
            })

        return CustomerData(**customer_params)
