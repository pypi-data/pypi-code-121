# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class sm_member(models.Model):
  _inherit = 'res.partner'
  _name = 'res.partner'

  reservation_count = fields.Integer("Reservations", compute='_compute_reservation_count')

  @api.multi
  def partner_reservations_return_action_to_open(self):
    """ This opens the xml view specified in xml_id for the current vehicle """
    self.ensure_one()
    xml_id = self.env.context.get('xml_id')
    children_ids = list()
    for child in self.child_ids:
      children_ids.append(child.id)
    if xml_id:
        res = self.env['ir.actions.act_window'].for_xml_id('sm_partago_usage', xml_id)
        res.update(
            context=dict(self.env.context, group_by=False),
            domain=['|', ('member_id', '=', self.id), ('member_id', 'in', children_ids)]
        )
        return res

  @api.multi
  def _compute_reservation_count(self):
    for partner in self:
      total_reservations = self.env['smp.sm_reservation_compute'].search_count([('member_id', '=', partner.id)])
      
      for child in partner.child_ids:
        total_reservations += self.env['smp.sm_reservation_compute'].search_count([('member_id', '=', child.id)])
      
      partner.reservation_count = total_reservations