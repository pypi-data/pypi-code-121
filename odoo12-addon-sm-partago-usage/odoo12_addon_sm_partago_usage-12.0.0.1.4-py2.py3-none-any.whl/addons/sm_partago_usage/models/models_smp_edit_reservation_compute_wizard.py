# -*- coding: utf-8 -*-

from datetime import datetime
import pytz

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils



class sm_edit_reservation_compute_wizard(models.TransientModel):
  _name = "smp.sm_edit_reservation_compute_wizard"

  def get_default_startTime(self):
    current_reservation = self.get_context_current_reservation()
    if current_reservation:
      return current_reservation.startTime
    return False
    
  def get_default_effectiveStartTime(self):
    current_reservation = self.get_context_current_reservation()
    if current_reservation:
      return current_reservation.effectiveStartTime
    return False
    
  def get_default_endTime(self):
    current_reservation = self.get_context_current_reservation()
    if current_reservation:
      return current_reservation.endTime
    return False
    
  def get_default_effectiveEndTime(self):
    current_reservation = self.get_context_current_reservation()
    if current_reservation:
      return current_reservation.effectiveEndTime
    return False

  startTime = fields.Datetime(string='Start Time', readonly=False, default=get_default_startTime)
  effectiveStartTime = fields.Datetime(string='Effective Start Time', readonly=False, default=get_default_effectiveStartTime)
  endTime = fields.Datetime(string='End Time', readonly=False, default=get_default_endTime)
  effectiveEndTime = fields.Datetime(string='Effective End Time', readonly=False, default=get_default_effectiveEndTime)

  def get_context_current_reservation(self):
    try:
      active_reservation_id = self.env.context['active_id']
    except:
      active_reservation_id = False
    return  self.env['smp.sm_reservation_compute'].browse(active_reservation_id)

  @api.multi
  def create_request(self):
    self.modify_dates()
    return True
        
  @api.model
  def modify_dates(self):
    current_reservation = self.get_context_current_reservation()
    if current_reservation:
      current_reservation.write({
        'startTime': self.startTime,
        'effectiveStartTime': self.effectiveStartTime,
        'endTime': self.endTime,
        'effectiveEndTime': self.effectiveEndTime,
        'ignore_update': True,
      })
      
    return True
