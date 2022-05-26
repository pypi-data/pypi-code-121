import json
from datetime import datetime
from decimal import Decimal

def checkKey(dict, key):
    try:
        if key in dict.keys():
            return True
        else:
            return False
    except:
        return False

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        elif isinstance(o, list):
            for i in xrange(len(o)):
                o[i] = self.default(o[i])
            return o
        elif isinstance(o, set):
            new_list = []
            for index, data in enumerate(o):
                new_list.append(self.default(data))
                
            return new_list
        elif isinstance(o, dict):
            for k in o.iterkeys():
                o[k] = self.default(o[k])
            return o
        elif isinstance(o, (datetime.date, datetime)):
            return o.isoformat()
        return super(DecimalEncoder, self).default(o)        