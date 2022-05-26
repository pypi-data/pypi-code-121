from odoo import http
from odoo import _
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
from odoo.addons.easy_my_coop_api.controllers.controllers import UserController as BaseAPIKeyController  # noqa
from odoo.addons.somconnexio.services.res_partner_service import ResPartnerService
from odoo.addons.somconnexio.services.contract_contract_service import ContractService
from odoo.addons.somconnexio.services import schemas
from odoo.exceptions import ValidationError
from pyopencell.client import Client
from pyopencell.exceptions import PyOpenCellAPIException
import base64
import logging
try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")


class APIKeyController(BaseAPIKeyController):
    @http.route(
        BaseAPIKeyController._root_path + "partner/check_sponsor",
        auth='api_key',
        methods=['GET']
    )
    @serialize_exception
    def check_sponsor(self, vat, sponsor_code, **kw):
        data = ResPartnerService(request).check_sponsor(vat, sponsor_code)
        return request.make_json_response(data)

    @http.route(
        BaseAPIKeyController._root_path + "contract",
        auth='api_key',
        methods=['GET'],
    )
    def get_contract(self, **params):
        v = Validator()
        if not v.validate(params, self.validator_search_contract(),):
            raise ValidationError(_('BadRequest {}').format(v.errors))
        service = ContractService(request.env)
        response = service.search(**params)
        return request.make_json_response(response)

    @staticmethod
    def validator_search_contract():
        return schemas.S_CONTRACT_SEARCH


class UserController(http.Controller):
    @http.route(
        ['/web/binary/download_invoice'], auth='user',
        methods=['GET'], website=False
    )
    @serialize_exception
    def download_invoice(self, invoice_number, **kw):
        try:
            invoice_response = Client().get(
                "/invoice", invoiceNumber=invoice_number, includePdf=True
            )
        except PyOpenCellAPIException:
            return request.not_found()
        invoice_base64 = invoice_response["invoice"]["pdf"]
        filecontent = base64.b64decode(invoice_base64)
        if not filecontent:
            return request.not_found()
        else:
            filename = "{}.pdf".format(invoice_number)
            return request.make_response(filecontent, [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition(filename))
            ])
