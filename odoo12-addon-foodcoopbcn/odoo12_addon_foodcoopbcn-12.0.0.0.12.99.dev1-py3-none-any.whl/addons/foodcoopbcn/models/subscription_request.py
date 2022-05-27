# -*- coding: utf-8 -*-
from odoo import fields, models, _


class SubscriptionRequest(models.Model):
    _inherit = 'subscription.request'

    unit_composition = fields.Integer(
        string = 'Unit composition',
        help = "How many people compose the consumption unit."
    )
    join_commission = fields.Selection(
        selection = [
            ('si', _('Sí, em ve de gust participar en alguna comissió')),
            ('puntual', _('Tinc disponibilitat per a tasques puntuals')),
            ('no', _('No em puc comprometre abans que obri el súper')),
        ],
        help = 'Which way would you like to participate?',
        string = "Join commission",
        required = True,
    )
    discovery_channel = fields.Selection(
        selection = [
            ('boca', _('Boca-orella')),
            ('fulleto', _('Fulletó')),
            ('radio', _('Ràdio')),
            ('tv', _('TV')),
            ('premsa', _('Premsa')),
            ('xarxes', _('Xarxes socials')),
            ('web', _('WEB')),
            ('buscador', _('Buscador d’internet')),
            ('altres', _('Altres'))
        ],
        help = 'How people find us.',
        string = 'Discovery channel',
        required = True,
    )
    newsletter_approved = fields.Boolean(
        string = 'Newsletter approved',
        required = True,
        default = False,
    )

    def get_required_field(self):
        req_fields = super(SubscriptionRequest, self).get_required_field()[:]
        req_fields.remove('iban')

        return req_fields
