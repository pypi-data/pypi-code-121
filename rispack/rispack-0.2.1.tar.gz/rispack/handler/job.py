from functools import wraps

from .record import RecordBuilder


def job(func):
    @wraps(func)
    def wrapper(event, context):
        items = event.get("Records") or [event]

        for item in items:
            record = RecordBuilder(item).build()

            func(record)

    return wrapper
