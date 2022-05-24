from .sqs import SQS, Publish

_sqs = None
_publishing = None

def get_msg_bus():
    global _sqs
    if _sqs is None:
        _sqs = SQS()
    return _sqs


def get_publish_bus():
    global _publishing
    if _publishing is None:
        _publishing = Publish()
    return _publishing
