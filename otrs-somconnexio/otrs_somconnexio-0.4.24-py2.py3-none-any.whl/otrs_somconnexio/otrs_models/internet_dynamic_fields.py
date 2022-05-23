# coding: utf-8

from pyotrs.lib import DynamicField

from otrs_somconnexio.otrs_models.provision_dynamic_fields import ProvisionDynamicFields


class InternetDynamicFields(ProvisionDynamicFields):

    def _build_specific_dynamic_fields(self):
        dynamic_fields = [
            self._econtract_id(),
            self._previous_service(),
            self._previous_provider(),
            self._previous_contract_address(),
            self._previous_contract_phone(),
            self._landline_number(),
            self._service_address(),
            self._service_city(),
            self._service_zip(),
            self._service_subdivision(),
            self._service_subdivision_code(),
            self._shipment_address(),
            self._shipment_city(),
            self._shipment_subdivision(),
            self._shipment_zip(),
            self._previous_owner_vat(),
            self._adsl_coverage(),
            self._mm_fiber_coverage(),
            self._orange_fiber_coverage(),
            self._vdf_fiber_coverage(),
            self._change_address(),
            self._change_address_provider(),
        ]
        dynamic_fields += self._build_specific_broadband_service_dynamic_fields()
        return dynamic_fields

    def _econtract_id(self):
        return DynamicField(name="IDContracte", value=self.service_data.order_id)

    def _previous_service(self):
        return DynamicField(name="serveiPrevi", value=self.service_data.previous_service)

    def _previous_provider(self):
        provider = None
        if self.service_data.type != "location_change":
            provider = self.service_data.previous_provider
        return DynamicField(name="proveidorPrevi", value=provider)

    def _landline_number(self):
        return DynamicField(name="telefonFixVell", value=self.service_data.phone_number)

    def _service_address(self):
        return DynamicField(name="direccioServei", value=self.service_data.service_address)

    def _service_city(self):
        return DynamicField(name="poblacioServei", value=self.service_data.service_city)

    def _service_zip(self):
        return DynamicField(name="CPservei", value=self.service_data.service_zip)

    def _service_subdivision(self):
        return DynamicField(name="provinciaServei", value=self.service_data.service_subdivision)

    def _service_subdivision_code(self):
        return DynamicField(name="codiProvinciaServei", value=self.service_data.service_subdivision_code)

    def _shipment_address(self):
        return DynamicField(name="direccioEnviament", value=self.service_data.shipment_address)

    def _shipment_city(self):
        return DynamicField(name="poblacioEnviament", value=self.service_data.shipment_city)

    def _shipment_subdivision(self):
        return DynamicField(name="provinciaEnviament", value=self.service_data.shipment_subdivision)

    def _shipment_zip(self):
        return DynamicField(name="CPenviament", value=self.service_data.shipment_zip)

    def _previous_owner_vat(self):
        return DynamicField(name="NIFNIEtitular", value=self.service_data.previous_owner_vat)

    def _adsl_coverage(self):
        return DynamicField(name="coberturaADSL", value=self.service_data.adsl_coverage)

    def _mm_fiber_coverage(self):
        return DynamicField(
            name="coberturaFibraMM",
            value=self.service_data.mm_fiber_coverage
        )

    def _vdf_fiber_coverage(self):
        return DynamicField(
            name="coberturaFibraVdf",
            value=self.service_data.vdf_fiber_coverage
        )

    def _orange_fiber_coverage(self):
        return DynamicField(
            name="coberturaFibraOrange",
            value=self.service_data.orange_fiber_coverage
        )

    def _previous_contract_phone(self):
        return DynamicField(name="telefonFixAntic", value=self.service_data.previous_contract_phone)

    def _previous_contract_address(self):
        return DynamicField(name="direccioServeiAntic", value=self.service_data.previous_contract_address)

    def _change_address(self):
        change_address = "yes" if self.service_data.type == "location_change" else "no"
        return DynamicField(name="canviUbicacioMateixTitular", value=change_address)

    def _change_address_provider(self):
        return DynamicField(name="proveidorPreviCU", value=self.service_data.previous_internal_provider)

    def _product(self):
        return DynamicField(
            name="productBA",
            value=self.service_data.product
        )
