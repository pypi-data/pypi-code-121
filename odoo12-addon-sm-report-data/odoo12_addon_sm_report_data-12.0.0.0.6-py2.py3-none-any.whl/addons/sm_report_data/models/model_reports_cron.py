# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class reports_cron(models.Model):
  _name = 'sm_report_data.reports_cron'

  @api.model
  def reports_cron_action(self):
    reports = self.env['sm_report_data.sm_report_data'].search([('active', '=', True)])
    for report in reports:
      report.send_report_via_email()
