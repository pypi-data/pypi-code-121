from datetime import date
from cc_py_commons.loads.load_schema import LoadSchema

def execute(freight_hub_json):
  freight_hub_json_copy = freight_hub_json.copy()
  freight_hub_json_copy['pickupDate'] = date.fromtimestamp(int(freight_hub_json['pickupDate'])/1000).isoformat()
  freight_hub_json_copy['deliveryDate'] = date.fromtimestamp(int(freight_hub_json['deliveryDate'])/1000).isoformat()
  return LoadSchema().load(freight_hub_json_copy)
