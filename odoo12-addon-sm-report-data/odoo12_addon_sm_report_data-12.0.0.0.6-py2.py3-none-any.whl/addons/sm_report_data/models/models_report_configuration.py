# -*- coding: utf-8 -*-
import pytz
import xlsxwriter
from odoo import models, fields, api
from odoo.tools.translate import _

try:
  from StringIO import StringIO
except ImportError:
  from io import StringIO
import base64

from io import BytesIO
from odoo.addons.sm_report_data.models.report_helper import report_helper
import time
from datetime import timedelta, datetime


class sm_report_data(models.Model):
  _name = 'sm_report_data.sm_report_data'

  name = fields.Char(string=_("Name"), required=True)
  report_model = fields.Many2one('ir.model', string=_("Report model"), required=True)
  recipient = fields.Many2one('res.partner', string="Destinataris", required=True)

  description = fields.Text()

  last_execution = fields.Date(string=_("Last execution"), default=time.strftime('%Y-%m-%d'))
  next_execution = fields.Date(string=_("Next execution"))
  final_date = fields.Date(string=_("Final date"))

  specific_search = fields.Boolean(string=_("Specific range (Days)"))
  general_range = fields.Selection([
    ('day', 'Days'),
    ('week', 'Weeks'),
    ('month', 'Months'),
    ('year', 'Years'),
  ], string='Range', default='day')

  daily_range = fields.Selection(
    [(num, str(num)) for num in range(1, 32)]
    , string=_("Number"), default=1)

  email_template = fields.Many2one('mail.template', string=_("Mail template"))
  email_subject = fields.Char(string=_("Email subject"))
  email_body = fields.Char(string=_("Email body"))

  active = fields.Boolean(string=_("Active"))

  report_helper = report_helper.get_instance()

  @api.model
  def send_email(self):
    if self.env.context:
      if 'active_ids' in self.env.context:
        models = self.env['sm_report_data.sm_report_data'].browse(self.env.context['active_ids'])
        if models.exists():
          for rec in models:
            rec.send_report_via_email()

  def send_report_via_email(self):
    try:
      self.send_report_via_email_inside()
    except:
      print("ERROR SENDING");

  def send_report_via_email_inside(self):
    if not self.next_execution:
      self.calculate_next_execute()

    next_exe = datetime.strptime(str(self.next_execution), '%Y-%m-%d')

    timezone = pytz.timezone('Europe/Madrid')
    date_time = datetime.now(tz=timezone)
    sys_date = datetime.date(date_time)

    if sys_date == next_exe.date():
      fp = BytesIO()
      workbook = xlsxwriter.Workbook(fp)
      worksheet = self.report_helper.generate_header(workbook)

      objects_to_iterate = self.get_objects_to_iterates()

      self.report_helper.fill_document(objects_to_iterate, worksheet)

      workbook.close()
      fp.seek(0)
      datas = base64.b64encode(fp.read())

      file_name = "Report-" + str(sys_date) + ".xlsx"

      attachment = []

      attachment_data = {
        'name': file_name,
        'datas_fname': file_name,
        'datas': datas,
        'res_model': "modelname",
      }

      id_new_attachment = self.env['ir.attachment'].create(attachment_data).id
      attachment.append(id_new_attachment)
      mail_template_name = "mail_template_reports_" + str(self.id)
      mail_template_name = mail_template_name.lower()
      mail_model = self.env['mail.template'].search(
        [("name", "=", mail_template_name)], limit=1)
      # Delete previously created attachments
      for attachment in mail_model.attachment_ids:
        attachment.unlink()
      mail_model.attachment_ids = [(4, id_new_attachment)]
      email_values = {'send_from_code': True}
      mail_model.with_context(email_values).send_mail(self.id, raise_exception=False, force_send=True)
      # self.env['ir.attachment'].search([('id', '=', id_new_attachment)]).unlink()
      self.last_execution = sys_date
      self.calculate_next_execute()

  def calculate_next_execute(self):
    range_execution = self.general_range
    initial_date = self.last_execution
    initial_date = datetime.strptime(str(initial_date), '%Y-%m-%d')
    days = self.daily_range
    if range_execution == "day":
      final_date = initial_date + timedelta(days=days)
    elif range_execution == "week":
      final_date = initial_date + timedelta(weeks=days)
    elif range_execution == "month":
      final_date = initial_date + timedelta(days * 365 / 12)
    elif range_execution == "year":
      final_date = initial_date + timedelta(days * 365)
    self.next_execution = final_date.strftime('%Y-%m-%d')

  def get_objects_to_iterates(self):
    initial_date = datetime.strptime(str(self.last_execution), '%Y-%m-%d')

    model = self.report_model.model

    days = self.daily_range
    range_execution = self.general_range

    if range_execution == "day":
      final_date = initial_date + timedelta(days=days)
    elif range_execution == "week":
      final_date = initial_date + timedelta(weeks=days)
    elif range_execution == "month":
      final_date = initial_date + timedelta(days * 365 / 12)
    elif range_execution == "year":
      final_date = initial_date + timedelta(days * 365)

    print('REPORT: filtering creating report!!!')
    print(str(initial_date))
    print(str(final_date))

    affected_objects = self.env[model].search(
      [
        ('effectiveStartTime', '>=', str(initial_date)),
        ('effectiveStartTime', '<', str(final_date)),
      ], order="id")

    print(str(affected_objects))

    # filtered_list = affected_objects.filtered(lambda r:
    #   r.related_current_car.vehicle_type == "van" or
    #   r.related_current_car.vehicle_type == "car")

    results = affected_objects.sorted(key=lambda r: r.id)

    return results

  @api.constrains('name', 'report_model', 'recipient')
  def _create_and_assign_template(self):
    for record in self:
      record.create_new_template()

  def create_new_template(self):
    if not self.email_template:
      if self.name and self.recipient and self.id:
        model_id = self.env['ir.model'].search(
          [("name", "=", "sm_report_data.sm_report_data")])

        data = {
          'model_id': model_id.id,
          'name': "mail_template_reports_" + str(self.id),
          'email_from': "info@sommobilitat.coop",
          'subject': "${object.email_subject}",
          'partner_to': self.recipient.id,
          'auto_delete': True,
          'body_html': "${object.email_body}"
        }

        new_template = self.env['mail.template'].create(data)
        self.email_template = new_template.id
