"""Created on 25 mars 2019.

@author: Aurele Durand
"""
import datetime, decimal
import enum
import pandas as pd
import numpy as np

from _collections_abc import dict_keys

from flask.json import JSONEncoder

from sqlalchemy.exc import OperationalError


class AlphaJSONEncoder(JSONEncoder):
    rules = {}

    def __init__(self, *args, **kwargs):
        super(AlphaJSONEncoder, self).__init__(*args, **kwargs)

        self.rules[np.int64] = int
        self.rules[np.bool_] = lambda o: o is True
        self.rules[datetime.datetime] = (
            lambda o: str(o.strftime("%Y-%m-%dT%H:%M:%S"))
            if "T" in str(o)
            else str(o.strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.rules[pd.DataFrame] = lambda o: o.to_json(orient="index")
        self.rules[bytes] = lambda o: str(o.decode("utf-8"))
        self.rules[dict_keys] = lambda o: list(o)
        self.rules[datetime.timedelta] = lambda o: str(o)
        self.rules[decimal.Decimal] = lambda o: str(o)
        self.rules[enum.Enum] = lambda o: str(o)
        self.rules[str] = lambda o: str(o)
        # self.rules[NameError] = lambda o:str(o)
        # self.rules[ValueError] = lambda o:str(o)
        # self.rules[TypeError] = lambda o:str(o)
        # self.rules[AttributeError] = lambda o:str(o)
        # self.rules[OperationalError] = lambda o:str(o)
        # self.rules[str] = lambda o:str(o)

    def default(self, o):  # pylint: disable=E0202
        if "<class " in str(o):
            return str(o)

        try:
            if hasattr(o, "to_json"):
                try:
                    output = o.to_json()
                    return output
                except Exception as ex:
                    print(ex)
                    return None
            for key_type, fct in self.rules.items():
                if isinstance(o, key_type):
                    returned_value = fct(o)
                    return returned_value
            try:
                iterable = iter(o)
            except:
                iterable = None
        except TypeError as ex:
            print(f"Cannot convert {o} to json: {ex}")
        else:
            if iterable is not None:
                return list(iterable)

        try:
            return JSONEncoder.default(self, o=o)
        except:
            o = str(o)
            try:
                return JSONEncoder.default(self, o=o)
            except:
                return o

        """results_json = {}
        if hasattr(model,"schema"):
            schema          = model.get_schema()
            structures      = schema(many=True) if not first else schema()
            results_json    = structures.dump(results)
        else:
            self.log.error('Missing schema for model <%s>'%str(model.__name__))"""
