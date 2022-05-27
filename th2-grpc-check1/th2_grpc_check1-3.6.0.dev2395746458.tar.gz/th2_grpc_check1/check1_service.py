from . import check1_pb2_grpc as importStub

class Check1Service(object):

    def __init__(self, router):
        self.connector = router.get_connection(Check1Service, importStub.Check1Stub)

    def createCheckpoint(self, request, timeout=None):
        return self.connector.create_request('createCheckpoint', request, timeout)

    def submitCheckRule(self, request, timeout=None):
        return self.connector.create_request('submitCheckRule', request, timeout)

    def submitCheckSequenceRule(self, request, timeout=None):
        return self.connector.create_request('submitCheckSequenceRule', request, timeout)

    def submitNoMessageCheck(self, request, timeout=None):
        return self.connector.create_request('submitNoMessageCheck', request, timeout)