import datetime
import decimal
from typing import Generator
from flask import json


class JSONEncoderCurstom(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        
        if isinstance(o, Generator):
            o = list(o)

        try:
            return super().default(o)
        except:
            return str(o)
