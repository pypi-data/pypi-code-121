from odoo import fields, models, _, api


class ConfirmSaleOrderWizard(models.TransientModel):
    _name = 'confirm.sale.order.wizard'
    sale_order_ids = fields.Many2many('sale.order')

    @api.multi
    def button_confirm(self):
        for order in self.sale_order_ids:
            order.action_confirm()
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        sale_order_ids = self.env.context['active_ids']
        defaults['sale_order_ids'] = sale_order_ids
        return defaults
