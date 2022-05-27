from . import act_template_pb2_grpc as importStub

class ActService(object):

    def __init__(self, router):
        self.connector = router.get_connection(ActService, importStub.ActStub)

    def placeOrderFIX(self, request, timeout=None, properties=None):
        return self.connector.create_request('placeOrderFIX', request, timeout, properties)

    def sendMessage(self, request, timeout=None, properties=None):
        return self.connector.create_request('sendMessage', request, timeout, properties)

    def placeQuoteRequestFIX(self, request, timeout=None, properties=None):
        return self.connector.create_request('placeQuoteRequestFIX', request, timeout, properties)

    def placeQuoteFIX(self, request, timeout=None, properties=None):
        return self.connector.create_request('placeQuoteFIX', request, timeout, properties)

    def placeOrderMassCancelRequestFIX(self, request, timeout=None, properties=None):
        return self.connector.create_request('placeOrderMassCancelRequestFIX', request, timeout, properties)

    def placeQuoteCancelFIX(self, request, timeout=None, properties=None):
        return self.connector.create_request('placeQuoteCancelFIX', request, timeout, properties)

    def placeQuoteResponseFIX(self, request, timeout=None, properties=None):
        return self.connector.create_request('placeQuoteResponseFIX', request, timeout, properties)

    def placeSecurityListRequestFIX(self, request, timeout=None, properties=None):
        return self.connector.create_request('placeSecurityListRequestFIX', request, timeout, properties)

    def placeSecurityListRequest(self, request, timeout=None, properties=None):
        return self.connector.create_request('placeSecurityListRequest', request, timeout, properties)