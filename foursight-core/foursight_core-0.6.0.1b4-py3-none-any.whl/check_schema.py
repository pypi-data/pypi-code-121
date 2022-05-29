import datetime


class CheckSchema(object):

    UUID_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

    def __init__(self):
        self.uuid = self.create_uuid()

    def create_uuid(self):
        return datetime.datetime.utcnow().strftime(self.UUID_FORMAT)

    def create_placeholder_check(self, check_name):
        return {
            'name': check_name,
            'uuid': self.uuid,
            'kwargs': {'uuid': self.uuid, 'primary': True},
            'status': 'PASS',  # so these show up green
            'summary': 'Check has not yet run',
            'description': 'If queued, this check will run with default arguments'
        }
