from python_framework import HttpClientConstant, HttpDomain

CLIENT_DID_NOT_SENT_ANY_MESSAGE = HttpClientConstant.CLIENT_DID_NOT_SENT_ANY_MESSAGE.replace(HttpDomain.CLIENT_CONTEXT, 'Queue')
ERROR_AT_CLIENT_CALL_MESSAGE = HttpClientConstant.ERROR_AT_CLIENT_CALL_MESSAGE.replace(HttpDomain.CLIENT_CONTEXT.lower(), HttpDomain.EMITTER_CONTEXT.lower())
