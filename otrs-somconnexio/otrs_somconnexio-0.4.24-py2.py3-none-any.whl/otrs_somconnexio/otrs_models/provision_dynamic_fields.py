# coding: utf-8

from pyotrs.lib import DynamicField


class ProvisionDynamicFields():

    def __init__(self, service_data, customer_data, otrs_process_id, otrs_activity_id):
        self.service_data = service_data
        self.customer_data = customer_data
        self.otrs_process_id = otrs_process_id
        self.otrs_activity_id = otrs_activity_id

    def all(self):
        dynamic_fields = [
            self._process_id(),
            self._activity_id(),
            self._first_name(),
            self._name(),
            self._vat_number(),
            self._iban(),
            self._phone(),
            self._mail(),
            self._previous_owner_name(),
            self._previous_owner_surname1(),
            self._previous_owner_full_name(),
            self._product(),
        ]
        dynamic_fields += self._build_specific_dynamic_fields()

        return [field for field in dynamic_fields if field.value]

    def _process_id(self):
        return DynamicField(name="ProcessManagementProcessID", value=self.otrs_process_id)

    def _activity_id(self):
        return DynamicField(name="ProcessManagementActivityID", value=self.otrs_activity_id)

    def _econtract_id(self):
        return DynamicField(name="IDContracte", value=self.service_data.order_id)

    def _first_name(self):
        return DynamicField("nomSoci", self.customer_data.first_name)

    def _name(self):
        return DynamicField("cognom1", self.customer_data.name)

    def _vat_number(self):
        return DynamicField(name="NIFNIESoci", value=self.customer_data.vat_number)

    def _mail(self):
        return DynamicField(name="correuElectronic", value=self.service_data.email)

    def _phone(self):
        return DynamicField(name="telefonContacte", value=self.customer_data.phone)

    def _iban(self):
        return DynamicField("IBAN", self.service_data.iban)

    def _previous_owner_name(self):
        return DynamicField(name="titular", value=self.service_data.previous_owner_name)

    def _previous_owner_surname1(self):
        return DynamicField(
            name="cognom1Titular",
            value=self.service_data.previous_owner_surname
        )

    def _previous_owner_full_name(self):
        full_name = ""
        if self.service_data.type == "location_change":
            full_name = "{} {}".format(
                self.service_data.previous_owner_name,
                self.service_data.previous_owner_surname
            )
        return DynamicField(
            name="nomCognomSociAntic",
            value=full_name
        )
