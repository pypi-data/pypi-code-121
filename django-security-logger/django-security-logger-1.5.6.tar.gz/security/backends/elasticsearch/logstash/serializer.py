try:
    import json
except ImportError:
    import simplejson as json


def serialize_message(message, metadata):
    return bytes(
        json.dumps({
            'message': message,
            'meta': metadata,
        }) + '\n', 'utf-8'
    )
