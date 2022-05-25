import logging

from odoo.addons.component.core import Component
from odoo.exceptions import MissingError
from odoo.fields import Date

from odoo import _

from . import schemas
from .vat_normalizer import VATNormalizer

_logger = logging.getLogger(__name__)


class ResPartnerService(Component):
    _inherit = "base.rest.service"
    _name = "res.partner.service"
    _usage = "partner"
    _collection = "emc.services"
    _description = """
        ResPartner service to expose the partners and filter by VAT number.
    """

    def get(self, _id):
        ref = str(_id)
        domain = [
            ("parent_id", "=", None),
            ("ref", "=", ref),
        ]

        _logger.info("search with domain {}".format(domain))
        partners = self.env["res.partner"].search(domain, limit=1)

        if not partners:
            raise MissingError(_("Partner with ref {} not found.".format(ref)))

        return self._to_dict(partners)

    def search(self, vat):
        domain = [
            ("parent_id", "=", None),
            ("vat", "ilike", VATNormalizer(vat).normalize()),
        ]

        _logger.info("search with domain {}".format(domain))
        partners = self.env["res.partner"].search(domain, limit=1)

        if not partners:
            raise MissingError(_("Partner with VAT {} not found.".format(vat)))

        return self._to_dict(partners)

    def check_sponsor(self, vat, sponsor_code):
        domain = [
            ("sponsorship_hash", "ilike", sponsor_code),
            ("vat", "ilike", VATNormalizer(vat).normalize()),
        ]
        partner = self.env["res.partner"].search(domain, limit=1)
        if not partner:
            result = "not_allowed"
            message = "invalid code or vat number"
        elif not partner.can_sponsor():
            result = "not_allowed"
            message = "maximum number of sponsees exceeded"
        else:
            result = "allowed"
            message = "ok"
        return {
            "result": result,
            "message": message
        }

    def _to_dict(self, partner):
        partner.ensure_one()
        return {
            "id": partner.id,
            "name": partner.name,
            "firstname": partner.firstname or "",
            "lastname": partner.lastname or "",
            "display_name": partner.lastname or "",
            "ref": partner.ref or "",
            "lang": partner.lang or "",
            "vat": partner.vat or "",
            "type": partner.type or "",
            "email": partner.email or "",
            "phone": partner.phone or "",
            "mobile": partner.mobile or "",
            "cooperator_register_number": partner.cooperator_register_number,
            "cooperator_end_date": Date.to_string(partner.cooperator_end_date) or "",
            "sponsor_id": partner.sponsor_id.id or 0,
            "coop_agreement_code": partner.coop_agreement_id.code or "",
            "sponsorship_code": partner.sponsorship_hash or "",
            "sponsees_number": partner.active_sponsees_number,
            "sponsees_max": partner.company_id.max_sponsees_number,
            "coop_candidate": partner.coop_candidate,
            "member": partner.member,
            "addresses": self._addresses_to_dict(partner)
        }

    def _addresses_to_dict(self, partner):
        """
        Convert Partner addresses objects in a list of address dicts
        removing the duplicated addresses.
        """
        addresses = partner.child_ids.filtered(
            lambda addr: addr.type in AddressService.ADDRESS_TYPES
        )
        addresses = addresses | partner
        addresses = addresses.mapped(lambda a: AddressService(self.env, a))
        addresses = list(set(addresses))
        return [addr.__dict__ for addr in addresses]

    def _validator_get(self):
        return schemas.S_RES_PARTNER_REQUEST_GET

    def _validator_return_get(self):
        return schemas.S_RES_PARTNER_RETURN_GET

    def _validator_search(self):
        return schemas.S_RES_PARTNER_REQUEST_SEARCH

    def _validator_return_search(self):
        return schemas.S_RES_PARTNER_RETURN_GET


# TODO: We can move this class in a separate file if we need it in other contexts.
class AddressService:
    ADDRESS_TYPES = ["service", "invoice", "delivery", "other"]

    def __init__(self, env, address):
        """
        TODO: Please, remove the `or "-"` when the data had been fixed.
        """
        self.street = address.street or "-"
        self.zip_code = address.zip or "-"
        self.city = address.city or "-"
        self.country = address.country_id.name or env.ref("base.es").name
        self.state = address.state_id.name or "-"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.__hash__() == other.__hash__()

    def _normalized_dict(self):
        normalized_dict = {}
        for k, v in self.__dict__.items():
            normalized_dict[k] = v.lower().strip()
        return normalized_dict

    def __hash__(self):
        return hash(str(self._normalized_dict()))
