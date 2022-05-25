from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fibre import MMFibreCoverage
from otrs_somconnexio.otrs_models.coverage.vdf_fibre import VdfFibreCoverage
from otrs_somconnexio.otrs_models.coverage.orange_fibre import OrangeFibreCoverage

from ..sc_test_case import SCTestCase

from ...otrs_factories.router_4G_data_from_crm_lead_line \
    import Router4GDataFromCRMLeadLine


class Router4GDataFromCRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.crm_lead_line_args = {
            'name': 'New CRMLeadLine',
            'description': 'description test',
            'product_id': self.ref('somconnexio.Router4G'),
            'mobile_isp_info': None,
            'broadband_isp_info': None,
        }

    def test_build(self):
        broadband_isp_info = self.env['broadband.isp.info'].create({
            "delivery_street": "Carrer Nogal",
            "delivery_street2": "55 Principal",
            "delivery_zip_code": "08008",
            "delivery_city": "Barcelona",
            "delivery_state_id": self.ref(
                'base.state_es_b'
            ),
            "delivery_country_id": self.ref(
                'base.es'
            ),
            'type': 'new',
            "service_street": "Calle Repet",
            "service_street2": "1 5º A",
            "service_zip_code": "01003",
            "service_city": "Madrid",
            "service_state_id": self.ref(
                'base.state_es_m'
            ),
            "service_country_id": self.ref(
                'base.es'
            ),
        })
        self.crm_lead_line_args['broadband_isp_info'] = broadband_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        self.env['crm.lead'].create({
            'name': 'Test Lead',
            'description': 'Test description',
            'iban': 'ES9420805801101234567891',
            'lead_line_ids': [(6, 0, [crm_lead_line.id])]
        })

        router_4G_data = Router4GDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(router_4G_data.order_id, crm_lead_line.id)
        self.assertEqual(router_4G_data.phone_number, '-')
        self.assertEqual(
            router_4G_data.service_address,
            broadband_isp_info.service_full_street)
        self.assertEqual(
            router_4G_data.service_city,
            broadband_isp_info.service_city)
        self.assertEqual(
            router_4G_data.service_zip,
            broadband_isp_info.service_zip_code)
        self.assertEqual(
            router_4G_data.service_subdivision,
            "Madrid")
        self.assertEqual(
            router_4G_data.service_subdivision_code,
            "ES-M")
        self.assertEqual(
            router_4G_data.shipment_address,
            broadband_isp_info.delivery_full_street)
        self.assertEqual(
            router_4G_data.shipment_city,
            broadband_isp_info.delivery_city)
        self.assertEqual(
            router_4G_data.shipment_zip,
            broadband_isp_info.delivery_zip_code)
        self.assertEqual(
            router_4G_data.shipment_subdivision,
            broadband_isp_info.delivery_state_id.name)
        self.assertEqual(router_4G_data.notes, crm_lead_line.lead_id.description)
        self.assertEqual(router_4G_data.iban, crm_lead_line.lead_id.iban)
        self.assertEqual(router_4G_data.email, crm_lead_line.lead_id.email_from)
        self.assertEqual(router_4G_data.product, crm_lead_line.product_id.default_code)
        self.assertEqual(
            router_4G_data.shipment_address,
            broadband_isp_info.delivery_full_street)
        self.assertEqual(
            router_4G_data.shipment_city,
            broadband_isp_info.delivery_city)
        self.assertEqual(
            router_4G_data.shipment_zip,
            broadband_isp_info.delivery_zip_code)
        self.assertEqual(
            router_4G_data.shipment_subdivision,
            broadband_isp_info.delivery_state_id.name)

    def test_change_address_build(self):
        service_supplier = self.browse_ref(
            "somconnexio.service_supplier_vodafone"
        )
        broadband_isp_info = self.env['broadband.isp.info'].create({
            "type": "location_change",
            "service_street": "Calle Repet",
            "service_street2": "1 5º A",
            "service_zip_code": "01003",
            "service_city": "Madrid",
            "service_state_id": self.ref('base.state_es_m'),
            "service_country_id": self.ref('base.es'),
            "service_supplier_id": service_supplier.id,
            "mm_fiber_coverage": MMFibreCoverage.VALUES[2][0],
            "vdf_fiber_coverage": VdfFibreCoverage.VALUES[3][0],
            "orange_fiber_coverage": OrangeFibreCoverage.VALUES[1][0],
            "adsl_coverage": ADSLCoverage.VALUES[6][0],
            "previous_contract_phone": "666666666",
            "previous_contract_address": "Calle Teper",
            "previous_provider": self.ref('somconnexio.previousprovider52'),
            "previous_phone_number": "666666666",
        })
        self.crm_lead_line_args['broadband_isp_info'] = broadband_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        router_4G_data = Router4GDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(router_4G_data.type, 'location_change')
        self.assertEqual(
            router_4G_data.previous_internal_provider, service_supplier.ref
        )
        self.assertEqual(router_4G_data.mm_fiber_coverage, MMFibreCoverage.VALUES[2][0])
        self.assertEqual(
            router_4G_data.vdf_fiber_coverage, VdfFibreCoverage.VALUES[3][0]
        )
        self.assertEqual(
            router_4G_data.orange_fiber_coverage, OrangeFibreCoverage.VALUES[1][0]
        )
        self.assertEqual(router_4G_data.adsl_coverage, ADSLCoverage.VALUES[6][0])
        self.assertEqual(router_4G_data.previous_contract_phone, "666666666")
        self.assertEqual(router_4G_data.previous_contract_address, "Calle Teper")
        self.assertEqual(router_4G_data.phone_number, "666666666")
