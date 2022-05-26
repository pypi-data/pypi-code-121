from odoo import models

try:
  from StringIO import StringIO
except ImportError:
  from io import StringIO

from odoo.addons.sm_report_data.models.report_helper import report_helper


class PartnerXlsx(models.AbstractModel):
  _name = 'report.sm_report_data.mossos'
  _inherit = 'report.report_xlsx.abstract'

  report_helper = report_helper.get_instance()

  def get_objects_to_iterate(self, partners):
    print("EXECUTING REPORT")
    from datetime import datetime, timedelta

    for obj in partners:
      initial_date = datetime.strptime(str(obj.last_execution), '%Y-%m-%d')

      days = obj.daily_range
      range_execution = obj.general_range

      if range_execution == "day":
        final_date = initial_date + timedelta(days=days)
      elif range_execution == "week":
        final_date = initial_date + timedelta(weeks=days)
      elif range_execution == "month":
        final_date = initial_date + timedelta(days * 365 / 12)
      elif range_execution == "year":
        final_date = initial_date + timedelta(days * 365)

      affected_objects = self.env[obj.report_model.model].search(
        [
          ('effectiveStartTime', '>=', str(initial_date)),
          ('effectiveStartTime', '<', str(final_date)),
        ], order="id")

      # filtered_list = affected_objects.filtered(lambda r:
      #   r.related_current_car.vehicle_type == "van" or
      #   r.related_current_car.vehicle_type == "car")

      return affected_objects.sorted(key=lambda r: r.id)

  def generate_xlsx_report(self, workbook, data, partners):
    worksheet = self.report_helper.generate_header(workbook)
    objects_to_iterate = self.get_objects_to_iterate(partners)
    self.report_helper.fill_document(objects_to_iterate, worksheet)
