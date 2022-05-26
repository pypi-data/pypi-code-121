from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils
class smp_usage_utils(object):

  __instance = None

  @staticmethod
  def get_instance():
    if smp_usage_utils.__instance is None:
      smp_usage_utils()
    return smp_usage_utils.__instance

  def __init__(self):
    if smp_usage_utils.__instance is not None:
      raise Exception("This class is a singleton!")
    else:
      smp_usage_utils.__instance = self

  def get_reservation_from_cc_and_start(self,parent,cc,start):
    if start and cc:
      query = [
        ('startTime','=',sm_utils.local_to_utc_datetime(start.strftime("%Y-%m-%d %H:%M:%S")))
      ]
      rel_cc = parent.env['smp.sm_car_config'].search([('name','=',cc)])
      if rel_cc.exists():
        query.append(('carconfig_id','=',rel_cc[0].id))
        existing_r = parent.env['smp.sm_reservation_compute'].search(query)
        if existing_r.exists():
          return existing_r[0]
    return False