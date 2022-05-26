# -*- coding: utf-8 -*-

from datetime import timezone
from datetime import datetime,timedelta
import pytz
import json

from odoo import models, api,fields
from odoo.tools.translate import _
from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils
from odoo.addons.sm_connect.models.models_sm_carsharing_db_utils import sm_carsharing_db_utils
from odoo.addons.sm_partago_invoicing.models.models_reservation_calculator import reservation_calculator
from odoo.addons.sm_partago_db.models.models_smp_db_utils import smp_db_utils

def _compute_reservation_params(parent, reservation):
  # Empty reservation params 
  reservation_params = {
    'creation_date_app': False,
    'lastmodified_date_app': False,
    'startTime': False,
    'endTime': False,
    'duration': 0,
    'effectiveStartTime': False,
    'effectiveEndTime': False,
    'effectiveDuration': 0,
    'fuel_consume': 0.0,
    'fuel_consume_watts': 0.0,
    'used_mileage': 0,
    'current_car': '',
    'credits': 0.0,
    'price': 0,
    'member_id': False,
    'related_company': '',
    'carconfig_id': False,
    'compute_cancelled': False,
    'fuel_consume_invoiced': 0, # Deprecated. remove when possible,
    'usage_mins_invoiced': 0,
    'non_usage_mins_invoiced': 0,
    'extra_usage_mins_invoiced': 0
  }
  if reservation:
    # Dates
    reservation_params['creation_date_app'] = sm_utils.local_to_utc_datetime(str(reservation['createdAt']).split('.')[0].replace("T"," "))
    reservation_params['lastmodified_date_app'] = sm_utils.local_to_utc_datetime(str(reservation['lastModifiedAt']).split('.')[0].replace("T"," "))
    reservation_params['startTime'] = sm_utils.local_to_utc_datetime(str(reservation['startTime']).split('.')[0].replace("T"," "))
    reservation_params['endTime'] = sm_utils.local_to_utc_datetime(str(reservation['endTime']).split('.')[0].replace("T"," "))
    reservation_params['duration'] = (reservation_params['endTime'] - reservation_params['startTime']).total_seconds() / 60.0
    # START: TripInfo
    tripinfo = reservation.get('tripInfo')
    if tripinfo:
      # Effective Start
      if tripinfo.get('effectiveStartTime'):
        effective_start_time = sm_utils.local_to_utc_datetime(str(tripinfo['effectiveStartTime']).split('.')[0].replace("T"," "))
      else:
        effective_start_time = reservation_params['startTime']
      reservation_params['effectiveStartTime'] = effective_start_time
      # Effective End
      if tripinfo.get('effectiveEndTime'):
        effective_end_time = sm_utils.local_to_utc_datetime(str(tripinfo['effectiveEndTime']).split('.')[0].replace("T"," "))
      else:
        effective_end_time = reservation_params['endTime']
      reservation_params['effectiveEndTime'] = effective_end_time
      # Effective Duration
      reservation_params['effectiveDuration'] = (effective_end_time - effective_start_time).total_seconds() / 60.0
      # Fuel Consume
      charged_percentage = tripinfo.get('chargedPercentage') or 0.0
      discharged_percentage = tripinfo.get('dischargedPercentage') or 0.0
      reservation_params['fuel_consume'] = discharged_percentage - charged_percentage
      # Fuel consume in watts
      charged = tripinfo.get('chargedEnergy') or 0.0
      discharged = tripinfo.get('dischargedEnergy') or 0.0
      reservation_params['fuel_consume_watts'] = discharged - charged
      # Used mileage
      reservation_params['used_mileage'] =tripinfo.get('distance') or 0
    # END: TripInfo
    # Current car
    current_car = reservation.get('carId')
    if current_car:
      reservation_params['current_car'] = current_car
    # Credits
    credits = reservation.get('credits')
    if credits:
      reservation_params['credits'] = credits
    # Price
    price = reservation.get('price')
    if price:
      reservation_params['credits'] = price
    # Related partner
    cs_person_index = reservation.get("personId")
    if cs_person_index:
      member = parent.env['res.partner'].search([('cs_person_index', '=', cs_person_index)])
      if member.exists():
        reservation_params['member_id'] = member.id
        if member.parent_id:
          reservation_params['related_company'] = member.parent_id.name
    # Related carconfig
    carconfig_app = reservation.get("resourceId")
    carconfigs_vc = parent.env['smp.sm_car_config'].search([('name', '=', carconfig_app)])
    if carconfigs_vc.exists():
      reservation_params['carconfig_id'] = carconfigs_vc[0].id
    # Reservation cancelled?
    compute_cancelled = reservation.get('isCancelled')
    if compute_cancelled:
      reservation_params['compute_cancelled'] = compute_cancelled
    # Calculated reservation global times
    new_calculated_attributes = reservation_calculator.get_general_values(reservation_params,'list')
    reservation_params['usage_mins_invoiced'] = new_calculated_attributes['usage_mins']
    reservation_params['non_usage_mins_invoiced'] = new_calculated_attributes['non_usage_mins']
    reservation_params['extra_usage_mins_invoiced'] = new_calculated_attributes['extra_usage_mins']
    return reservation_params
  return False

class sm_reservation_wizard(models.TransientModel):
  _name = "smp.sm_reservation_wizard"

  from_q_date = fields.Date(string=_("From"))
  till_q_date = fields.Date(string=_("Till"))
  update_only_car = fields.Boolean(string=_("Update only car"))

  @api.multi
  def create_request(self):
    self.ensure_one()
    self.compute_reservations(self,self.from_q_date,self.till_q_date,update_only_car=self.update_only_car)
    return True

  @staticmethod
  def compute_reservations(parent,from_q=False,till_q=False,update_only_car = False,update_self=False):
    now_date = datetime.now()
    comp = False
    if from_q:
      from_q = from_q.strftime('%Y-%m-%d') + "T00:00:00.00"
    else:
      from_q = now_date.strftime('%Y-%m-%d') + "T00:00:00.00"
    if till_q:
      till_q = till_q.strftime('%Y-%m-%d') + "T00:00:00.00"
    else:
      till_q = now_date.strftime('%Y-%m-%d') + "T00:00:00.00"
    app_db_utils = smp_db_utils.get_instance(parent)
    reservations_data_grouped = app_db_utils.get_app_reservations_by_group(parent,from_q,till_q)
    if reservations_data_grouped:
      for reservations_data in reservations_data_grouped.values():
        for reservation in reservations_data:
          # SETUP OBJECT TO WRITE
          res_params = _compute_reservation_params(parent, reservation)
          if res_params:
            res_id = reservation.get("id")
            # self
            if update_self:
              if parent.name == res_id:
                comp = parent
            # new/existing
            else: 
              comp = sm_utils.get_create_existing_model(parent.env['smp.sm_reservation_compute'],
                [('name', '=', res_id)],{'name': res_id, 'compute_invoiced': False,
                'compute_forgiven': False, 'ignore_update': False})
            # UPDATE OBJECT
            if comp:
              # Only car
              if update_only_car:
                comp.write({
                  'current_car' : res_params['current_car']
                })
              # All params
              else:
                if not comp.ignore_update and not comp.compute_invoiced and not comp.compute_forgiven:
                  comp.write(res_params)

          # on each iteration we reset comp for being setup again
          comp = False