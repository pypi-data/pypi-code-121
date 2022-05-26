from odoo import models,api
from odoo.addons.sm_partago_usage.models.models_smp_reservation_wizard import sm_reservation_wizard

class smp_usage_cron(models.Model):
  _name = 'sm_partago_usage.smp_usage_cron'

  @api.model
  def fetch_reservations(self):
    sm_reservation_wizard.compute_reservations(self)