# -*- coding: utf-8 -*-

import time
from datetime import datetime

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.sm_maintenance.models.models_sm_resources import sm_resources
from odoo.addons.sm_partago_invoicing.models.models_reservation_calculator import reservation_calculator
from odoo.addons.sm_connect.models.models_sm_carsharing_db_utils import sm_carsharing_db_utils
from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils

class smp_reservation_compute(models.Model):
  _name = 'smp.sm_reservation_compute'

  name = fields.Char(string=_("Name"), required=True)
  name_nice = fields.Char(string=_("Name (Invoice line)"), compute="_get_compute_name_nice", store=False)
  member_id = fields.Many2one('res.partner', string=_("Member"))
  cs_user_type = fields.Char(string=_("cs user type"),compute="_get_cs_user_type", store=False)
  carconfig_id = fields.Many2one('smp.sm_car_config', string=_("caConfig (App DB)"))
  startTime = fields.Datetime(string=_("Start"),readonly=True)
  endTime = fields.Datetime(string=_("End"),readonly=True)
  effectiveStartTime = fields.Datetime(string=_("Effective Start"),readonly=True)
  effectiveEndTime = fields.Datetime(string=_("Effective End"),readonly=True)
  duration = fields.Float(string=_("Duration"))
  effectiveDuration = fields.Float(string=_("Effective Duration"))
  fuel_consume = fields.Float(string=_("Fuel consume (%)"))
  fuel_consume_watts = fields.Float(string=_("Fuel consume (kWh)"))
  used_mileage = fields.Float(string=_("Used mileage"))
  compute_cancelled = fields.Boolean(string=_("Compute cancelled"))
  compute_unused = fields.Boolean(_("Compute unused"))
  ignore_update = fields.Boolean(string=_("Ignore update"))
  usage_mins_invoiced = fields.Float(string=_("Used mins (Total)"))
  non_usage_mins_invoiced = fields.Float(string=_("Not used mins (Total)"))
  extra_usage_mins_invoiced = fields.Float(string=_("Extra used mins (Total)"))
  observations = fields.Text(string=_("Observations"))
  current_car = fields.Char(_("Associated car (App DB)"))
  related_current_car = fields.Many2one('fleet.vehicle', string=_("Associated car (CS Structure)"),
    compute="_get_related_associated_car",store=False)
  related_company = fields.Char(string=_("Company (Name)"))
  related_company_object = fields.Many2one('res.partner', string=_("Company (Relation)"), compute="set_company_object")
  credits = fields.Float(_("Credits"))
  price = fields.Float(_("Price"))

  cs_carconfig_id = fields.Many2one('sm_carsharing_structure.cs_carconfig', string=_("Associated carConfig (CS Structure)"),
    compute="_get_cs_carconfig_id",store=True)

  cs_production_unit_id = fields.Many2one('sm_carsharing_structure.cs_production_unit', string=_("Associated production unit (CS Structure)"),
    compute="_get_cs_production_unit_id",store=True)

  creation_date_app = fields.Datetime(string=_("Creation Date"),readonly=True)
  lastmodified_date_app = fields.Datetime(string=_("LastModified Date"),readonly=True)

  # Deprecated. Get this trough API now.
  initial_fuel_level = fields.Float(string=_("Initial fuel level"))
  final_fuel_level = fields.Float(string=_("Final fuel level"))

  _order = "startTime desc"
  
  @api.constrains('name')
  def _check_name_unique(self):
    names_found = self.env['smp.sm_reservation_compute'].search([('id', '!=', self.id),('name', '=', self.name)])
    if names_found.exists(): 
      raise ValidationError(_("Name must be unique"))

  @api.depends('related_company')
  def set_company_object(self):
    for record in self:
      current_company_text = record.related_company
      if current_company_text:
        company_object = self.env['res.partner'].search([
          ('name', '=', current_company_text)
        ])
        if company_object:
          record.related_company_object = company_object[0].id

  @api.model
  def fetch_update_reservation_data_from_action(self):
    if self.env.context:
      if 'active_ids' in self.env.context:
        computes = self.env['smp.sm_reservation_compute'].browse(self.env.context['active_ids'])
        if computes.exists():
          for compute in computes:
            compute.fetch_update_reservation_data(False)

  @api.model
  def fetch_update_reservation_car_data_from_action(self):
    if self.env.context:
      if 'active_ids' in self.env.context:
        computes = self.env['smp.sm_reservation_compute'].browse(self.env.context['active_ids'])
        if computes.exists():
          for compute in computes:
            compute.fetch_update_reservation_data(True)

  def fetch_update_reservation_data(self,update_only_car_bool = False):
    if self.startTime and self.endTime:
      self.env["smp.sm_reservation_wizard"].compute_reservations(
        parent=self, from_q=self.startTime, till_q=self.endTime,update_only_car = update_only_car_bool,update_self=True)

  def get_reservation_dbcar_obj(self):
    if not self.related_current_car:
      rel_carconfig = self.carconfig_id
      if rel_carconfig:
        return rel_carconfig.rel_car_id
      return False
    else:
      return self.related_current_car

  def get_cs_carconfig_obj(self):
    if self.carconfig_id.id != False:
      rel_cs_carconfig = self.env['sm_carsharing_structure.cs_carconfig'].search([('db_carconfig_id','=',self.carconfig_id.id)])
      if rel_cs_carconfig.exists():
        return rel_cs_carconfig[0]
    return False

  @api.depends('current_car')
  def _get_related_associated_car(self):
    related_current_car = None
    for record in self:
      if record.current_car:
        related_current_car_db = self.env['smp.sm_car'].search([
          ('name', '=', record.current_car)
        ])
        if related_current_car_db.exists():
          related_current_car_cs = self.env['fleet.vehicle'].search([
            ('db_car_id', '=', related_current_car_db.id)
          ])
          if related_current_car_cs.exists():
            record.related_current_car = related_current_car_cs[0].id

  @api.depends('carconfig_id')
  def _get_cs_carconfig_id(self):
    related_cs_cc = None
    for record in self:
      if record.carconfig_id:
        related_cs_cc = self.env['sm_carsharing_structure.cs_carconfig'].search([
          ('db_carconfig_id', '=', record.carconfig_id.id)
        ])
        if related_cs_cc.exists():
          record.cs_carconfig_id = related_cs_cc[0].id

  @api.depends('cs_carconfig_id')
  def _get_cs_production_unit_id(self):
    related_cs_cc = None
    for record in self:
      if record.cs_carconfig_id:
        record.cs_production_unit_id = record.cs_carconfig_id.production_unit_id.id

  @api.constrains('effectiveStartTime', 'effectiveEndTime', 'startTime', 'endTime')
  def update(self):
    for record in self:
      self.update_duration(record)

  def update_duration(self, record):
    fmt = '%Y-%m-%d %H:%M:%S'

    effective_end = datetime.strptime(str(record.effectiveEndTime), fmt)
    effective_start = datetime.strptime(str(record.effectiveStartTime), fmt)

    effective_end_ts = time.mktime(effective_end.timetuple())
    effective_start_ts = time.mktime(effective_start.timetuple())

    effective_duration = int(effective_end_ts - effective_start_ts) / 60

    end = datetime.strptime(str(record.endTime), fmt)
    start = datetime.strptime(str(record.startTime), fmt)

    end_ts = time.mktime(end.timetuple())
    start_ts = time.mktime(start.timetuple())

    duration = int(end_ts - start_ts) / 60

    self.write_invoiced_parameters(record)

    record.write({
      'duration': duration,
      'effectiveDuration': effective_duration
    })

  @api.depends('member_id')
  def _get_cs_user_type(self):
    for record in self:
      record.cs_user_type = str(record.member_id.cs_user_type)

  @api.depends('startTime', 'effectiveStartTime', 'carconfig_id')
  def _get_compute_name_nice(self):
    # calculate invoice line name
    for record in self:
      if record.effectiveStartTime < record.startTime:
        starttimecalc = record.effectiveStartTime
      else:
        starttimecalc = record.startTime
      start_time = sm_utils.utc_to_local_datetime(str(starttimecalc))
      start_time_str = start_time.strftime("%H:%M-%d/%m/%y")
      record.name_nice = record.carconfig_id.carconfig_name + \
        '-[' + start_time_str + ']'

  def write_invoiced_parameters(self, compute):
    update_values = reservation_calculator.get_general_values(compute, 'object')
    compute.write({
      'usage_mins_invoiced': update_values['usage_mins'],
      'non_usage_mins_invoiced': update_values['non_usage_mins'],
      'extra_usage_mins_invoiced': update_values['extra_usage_mins']
    })

  def get_edit_wizard_view(self):
    view_ref = self.env['ir.ui.view'].sudo().search(
      [('name', '=', 'sm_partago_usage.edit_reservation_compute_wizard.form')])
    return view_ref.id

  @api.multi
  def create_edit_reservation_compute_wizard(self):
    if self.env.context:
      return {
        'type': 'ir.actions.act_window',
        'name': "Edit reservation compute",
        'res_model': 'smp.sm_edit_reservation_compute_wizard',
        'view_type': 'form',
        'view_mode': 'form',
        'view_id': self.get_edit_wizard_view(),
        'target': 'new',
        'context': self.env.context
      }

  def view_on_app_action(self):
    company = self.env.user.company_id
    return {
      'type': 'ir.actions.act_url',
      'url': '%s/admin/#/reservation/%s' % (company.sm_carsharing_api_credentials_cs_url,self.name),
      'target': 'blank'
    }
