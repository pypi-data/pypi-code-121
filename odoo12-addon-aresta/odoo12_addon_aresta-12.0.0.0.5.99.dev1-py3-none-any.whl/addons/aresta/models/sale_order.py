from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Field used on sale reports pivot view
    pos_name = fields.Char()

    # Field shown on sales view in order to facilitate all sale points
    pos_id = fields.Many2one(
        'pos.config',
        string='POS name'
    )

    @api.model
    def _prepare_from_pos(self, order_data):
        vals = super()._prepare_from_pos(order_data)

        res_partner = self.env['res.partner'].search([
            ('id', '=', vals["partner_id"])
        ])
        carrier_id = res_partner.property_delivery_carrier_id.id

        pos_session = self.env["pos.session"]
        session = pos_session.browse(order_data["pos_session_id"])

        vals["pos_name"] = session.config_id.name
        vals["pos_id"] = session.config_id.id
        vals["carrier_id"] = carrier_id
        return vals

    def _write(self, values):
        if 'pos_id' in values:
            pos = self.env['pos.config'].search([
                ('id', '=', values["pos_id"])
            ])
            self.write({"pos_name": pos.name})
        return super(SaleOrder, self)._write(values)
