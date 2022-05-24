from .. import CoreService_pb2 as pb
from ..utils import Utils


class PersonalAccessToken:
    def __init__(self, stub, pat):
        self._pat = pat
        self._stub = stub

    def revoke(self):
        request = pb.TokenRequest()
        request.token_id = self._pat.id
        self._stub.RevokeToken(request)

    @property
    def id(self):
        return self._pat.id

    @property
    def name(self):
        return self._pat.name

    @property
    def description(self):
        return self._pat.description

    @property
    def expiry_date(self):
        return Utils.timestamp_to_string(self._pat.expiry_date)

    @property
    def last_used(self):
        return Utils.timestamp_to_string(self._pat.last_used)

    @property
    def creation_time(self):
        return Utils.timestamp_to_string(self._pat.creation_time)

    def __repr__(self):
        return Utils.pretty_print_proto(self._pat)
