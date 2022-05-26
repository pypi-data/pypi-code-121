from odoo import models


class AccountAsset(models.Model):
    _inherit = ['account.asset', 'mail.thread']
    _name = 'account.asset'
