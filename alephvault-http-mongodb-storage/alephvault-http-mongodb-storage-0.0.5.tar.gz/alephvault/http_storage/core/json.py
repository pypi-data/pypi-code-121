import typing as t
from flask import current_app as app
from flask.json import JSONEncoder
from datetime import datetime, date
from bson import ObjectId
from .formats import *


class MongoDBEnhancedEncoder(JSONEncoder):
    """
    This is an enhancement over a Flask's JSONEncoder but with
    adding the encoding of an ObjectId to string, and custom
    encodings for the date and datetime types.
    """

    def default(self, o: t.Any) -> t.Any:
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            use_splitseconds = getattr(app, 'timestamp_with_splitseconds', False)
            return o.strftime(DATETIME_FORMATS[0] if use_splitseconds else DATETIME_FORMATS[2])
        elif isinstance(o, date):
            return o.strftime(DATE_FORMAT)
        return super().default(o)
