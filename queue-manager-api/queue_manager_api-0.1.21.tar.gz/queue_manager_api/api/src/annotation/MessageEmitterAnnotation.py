import requests, time
from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework import (
    FlaskManager,
    ConverterStatic,
    FlaskUtil,
    ClientUtil,
    LogConstant,
    OpenApiManager,
    ConfigurationKeyConstant,
    HttpDomain,
    Serializer,
    GlobalException,
    HttpStatus
)

try:
    import AnnotationUtil
    import HttpEmitterConstant, MessageConstant, EmitterConstant
    import MessageDto
except:
    from queue_manager_api.api.src.util import AnnotationUtil
    from queue_manager_api.api.src.dto import MessageDto
    from queue_manager_api.api.src.constant import EmitterConstant
    from queue_manager_api.api.src.constant import HttpEmitterConstant
    from queue_manager_api.api.src.constant import MessageConstant


DEFAULT_TIMEOUT = 2


@Function
def MessageEmitter(
    *resourceArgs,
    url = EmitterConstant.URL,
    headers = None,
    timeout = DEFAULT_TIMEOUT,
    logRequest = False,
    logResponse = False,
    enabled = None,
    muteLogs = None,
    eventContext = HttpDomain.EMITTER_CONTEXT,
    **resourceKwargs
):
    def Wrapper(OuterClass, *outterArgs, **outterKwargs):
        resourceUrl = url
        resourceHeaders = ConverterStatic.getValueOrDefault(headers, dict())
        resourceTimeout = timeout
        resourceEventContext = eventContext
        resourceLogRequest = logRequest
        resourceLogResponse = logResponse
        resourceEnabled = enabled
        resourceMuteLogs = muteLogs
        log.wrapper(MessageEmitter, f'''wrapping {OuterClass.__name__}(*{outterArgs}, **{outterKwargs})''')
        api = FlaskManager.getApi()
        class InnerClass(OuterClass):
            url = resourceUrl
            headers = resourceHeaders
            def __init__(self, *args, **kwargs):
                log.wrapper(OuterClass, f'in {InnerClass.__name__}.__init__(*{args},**{kwargs})')
                OuterClass.__init__(self, *args,**kwargs)
                AnnotationUtil.initializeComunicationLayerResource(
                    resourceInstance = self,
                    api = api,
                    timeout = resourceTimeout,
                    enabled = resourceEnabled,
                    muteLogs = resourceMuteLogs,
                    logRequest = resourceLogRequest,
                    logResponse = resourceLogResponse,
                    resourceEnabledConfigKey = ConfigurationKeyConstant.API_EMITTER_ENABLE,
                    resourceMuteLogsConfigKey = ConfigurationKeyConstant.API_EMITTER_MUTE_LOGS,
                    resourceTimeoutConfigKey = ConfigurationKeyConstant.API_EMITTER_TIMEOUT
                )
                self.queueManager = api.queueManager
            def emit(self, *args, **kwargs):
                raise ClientUtil.HttpClientEvent(HttpDomain.Verb.POST, *args, eventContext=resourceEventContext, **kwargs)
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


class EmitterMethodConfig:
    def __init__(self,
        url = None,
        headers = None,
        requestHeaderClass = None,
        requestParamClass = None,
        requestClass = None,
        responseClass = None,
        returnOnlyBody = None,
        timeout = DEFAULT_TIMEOUT,
        propagateAuthorization = None,
        propagateApiKey = None,
        propagateSession = None,
        produces = None,
        consumes = None,
        logRequest = None,
        logResponse = None,
        enabled = None,
        muteLogs = None
    ):
        self.url = url
        self.headers = headers
        self.requestHeaderClass = requestHeaderClass
        self.requestParamClass = requestParamClass
        self.requestClass = requestClass
        self.responseClass = responseClass
        self.returnOnlyBody = returnOnlyBody
        self.timeout = timeout
        self.propagateAuthorization = propagateAuthorization
        self.propagateApiKey = propagateApiKey
        self.propagateSession = propagateSession
        self.produces = produces
        self.consumes = consumes
        self.logRequest = logRequest
        self.logResponse = logResponse
        self.enabled = enabled
        self.muteLogs = muteLogs


@Function
def MessageEmitterMethod(
    *methodArgs,
    url = EmitterConstant.URL,
    headers = None,
    requestHeaderClass = None,
    requestParamClass = None,
    requestClass = None,
    responseClass = None,
    returnOnlyBody = True,
    timeout = None,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logRequest = True,
    logResponse = True,
    enabled = True,
    muteLogs = False,
    debugIt = False,
    muteStacktraceOnBusinessRuleException = True,
    queueKey = None,
    messageHeaders = None,
    **methodKwargs
):
    resourceMethodConfig = EmitterMethodConfig(
        url = url,
        headers = headers,
        requestHeaderClass = requestHeaderClass,
        requestParamClass = requestParamClass,
        requestClass = requestClass,
        responseClass = responseClass,
        returnOnlyBody = returnOnlyBody,
        timeout = timeout,
        propagateAuthorization = False,
        propagateApiKey = False,
        propagateSession = False,
        produces = produces,
        consumes = consumes,
        logRequest = logRequest,
        logResponse = logResponse,
        enabled = enabled,
        muteLogs = muteLogs
    )
    def innerMethodWrapper(resourceInstanceMethod, *innerMethodArgs, **innerMethodKwargs) :
        wrapperManager = AnnotationUtil.InnerMethodWrapperManager(
            wrapperType = MessageEmitterMethod,
            resourceInstanceMethod = resourceInstanceMethod,
            timeout = timeout,
            enabled = enabled,
            muteLogs = muteLogs,
            logRequest = logRequest,
            logResponse = logResponse,
            resourceTypeName = FlaskManager.KW_EMITTER_RESOURCE,
            resourceEnabledConfigKey = ConfigurationKeyConstant.API_EMITTER_ENABLE,
            resourceMuteLogsConfigKey = ConfigurationKeyConstant.API_EMITTER_MUTE_LOGS,
            resourceTimeoutConfigKey = ConfigurationKeyConstant.API_EMITTER_TIMEOUT
        )
        resourceInstanceMethodMuteStacktraceOnBusinessRuleException = muteStacktraceOnBusinessRuleException
        resourceMethodMessageHeaders = messageHeaders
        resourceMethodQueueKey = queueKey
        resourceMethodConfig.wrapperManager = wrapperManager
        def post(
            resourceInstance,
            body = None,
            url = None,
            headers = None,
            params = None,
            timeout = None,
            logRequest = False,
            messageKey = None,
            queueKey = resourceMethodQueueKey,
            groupKey = None,
            messageHeaders = None,
            **kwargs
        ):
            verb = HttpDomain.Verb.POST
            url, params, headers, body, timeout, logRequest = ClientUtil.parseParameters(
                resourceInstance,
                resourceMethodConfig,
                url,
                params,
                headers,
                Serializer.getObjectAsDictionary(
                    MessageDto.MessageRequestDto(
                        key = messageKey,
                        queueKey = queueKey,
                        groupKey = groupKey,
                        headers = {
                            **ConverterStatic.getValueOrDefault(resourceMethodMessageHeaders, dict()),
                            **ConverterStatic.getValueOrDefault(messageHeaders, dict())
                        },
                        content = body
                    )
                ),
                timeout,
                resourceMethodConfig.wrapperManager.shouldLogRequest()
            )
            doLogRequest(verb, url, body, params, headers, logRequest, kwargs)
            emitterMethodResponse = requests.post(
                url,
                params = params,
                headers = headers,
                json = body,
                timeout = timeout,
                **kwargs
            )
            return emitterMethodResponse

        def doLogRequest(verb, url, body, params, headers, logRequest, requestKwargs):
            log.info(resourceInstanceMethod, f'{LogConstant.EMITTER_SPACE}{verb}{c.SPACE_DASH_SPACE}{url}')
            if logRequest:
                parsetRequestKwargs = {} if ObjectHelper.isEmpty(requestKwargs) else {'requestKwargs': {**requestKwargs}}
                log.prettyJson(
                    resourceInstanceMethod,
                    LogConstant.EMITTER_REQUEST,
                    {
                        'headers': ConverterStatic.getValueOrDefault(headers, dict()),
                        'query': ConverterStatic.getValueOrDefault(params, dict()),
                        'body': ConverterStatic.getValueOrDefault(body, dict()),
                        **parsetRequestKwargs
                    },
                    condition = True,
                    logLevel = log.INFO
                )

        HTTP_CLIENT_RESOLVERS_MAP = {
            HttpDomain.Verb.POST : post
        }
        def innerResourceInstanceMethod(*args, **kwargs):
            f'''(*args, {FlaskUtil.KW_HEADERS}={{}}, {FlaskUtil.KW_PARAMETERS}={{}}, **kwargs)'''
            wrapperManager.updateResourceInstance(args)
            resourceMethodConfig.logRequest = wrapperManager.shouldLogRequest()
            httpClientResolversMap = HTTP_CLIENT_RESOLVERS_MAP
            messageCreationRequestKey = kwargs.get(MessageConstant.MESSAGE_KEY_CLIENT_ATTRIBUTE_NAME)
            if ObjectHelper.isNone(messageCreationRequestKey):
                messageCreationRequestKey = f'{f"{time.time():0<10}".replace(c.DOT, c.DASH)}{c.DASH}{Serializer.newUuid()}'
            messageCreationRequestGroupKey = ConverterStatic.getValueOrDefault(
                kwargs.get(MessageConstant.GROUP_KEY_CLIENT_ATTRIBUTE_NAME),
                messageCreationRequestKey
            )
            messageCreationRequestHeaders = kwargs.get(MessageConstant.MESSAGE_HEADERS_KEY_CLIENT_ATTRIBUTE_NAME, {})

            completeResponse = [
                MessageDto.MessageCreationRequestDto(
                    key = messageCreationRequestKey,
                    queueKey = resourceMethodQueueKey,
                    groupKey = messageCreationRequestGroupKey
                ),
                {},
                HttpStatus.CREATED
            ]

            emitterArgs = (
                args,
                kwargs,
                wrapperManager,
                requestHeaderClass,
                requestParamClass,
                requestClass,
                responseClass,
                produces,
                httpClientResolversMap,
                returnOnlyBody,
                debugIt,
                messageCreationRequestKey,
                messageCreationRequestGroupKey,
                messageCreationRequestHeaders,
                resourceInstanceMethodMuteStacktraceOnBusinessRuleException
            )

            currentRequestUrl = FlaskUtil.safellyGetUrl()
            if ObjectHelper.isNotNone(currentRequestUrl):
                wrapperManager.resourceInstance.queueManager.runInAThread(
                    *(
                        resolveEmitterCallWithinAContext,
                        *emitterArgs,
                        currentRequestUrl,
                        FlaskUtil.safellyGetVerb(),
                        FlaskUtil.safellyGetHeaders(),
                        FlaskUtil.safellyGetArgs(),
                        FlaskUtil.safellyGetRequestBody()
                    )
                )
            else:
                log.debug(wrapperManager.resourceInstanceMethod, f'''The context "{currentRequestUrl}" didnt't started properlly. Running without a context by default''')
                wrapperManager.resourceInstance.queueManager.runInAThread(resolveEmitterCall, *emitterArgs)

            if wrapperManager.shouldLogResponse():
                resourceMethodResponseStatus = completeResponse[-1]
                resourceMethodResponseHeaders = completeResponse[1]
                resourceMethodResponseBody = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : HttpStatus.map(resourceMethodResponseStatus).enumName}
                log.prettyJson(
                    wrapperManager.resourceInstanceMethod,
                    LogConstant.EMITTER_RESPONSE,
                    {
                        'headers': resourceMethodResponseHeaders,
                        'body': Serializer.getObjectAsDictionary(resourceMethodResponseBody, muteLogs=not debugIt),
                        'status': resourceMethodResponseStatus
                    },
                    condition = True,
                    logLevel = log.INFO
                )
            if returnOnlyBody:
                return completeResponse[0]
            else:
                return completeResponse
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, wrapperManager.resourceInstanceMethod)
        innerResourceInstanceMethod.url = resourceMethodConfig.url
        innerResourceInstanceMethod.headers = resourceMethodConfig.headers
        innerResourceInstanceMethod.requestHeaderClass = resourceMethodConfig.requestHeaderClass
        innerResourceInstanceMethod.requestParamClass = resourceMethodConfig.requestParamClass
        innerResourceInstanceMethod.requestClass = resourceMethodConfig.requestClass
        innerResourceInstanceMethod.responseClass = resourceMethodConfig.responseClass
        innerResourceInstanceMethod.returnOnlyBody = resourceMethodConfig.returnOnlyBody
        innerResourceInstanceMethod.timeout = resourceMethodConfig.timeout
        innerResourceInstanceMethod.propagateAuthorization = resourceMethodConfig.propagateAuthorization
        innerResourceInstanceMethod.propagateApiKey = resourceMethodConfig.propagateApiKey
        innerResourceInstanceMethod.propagateSession = resourceMethodConfig.propagateSession
        innerResourceInstanceMethod.produces = resourceMethodConfig.produces
        innerResourceInstanceMethod.consumes = resourceMethodConfig.consumes
        innerResourceInstanceMethod.logRequest = resourceMethodConfig.logRequest
        innerResourceInstanceMethod.logResponse = resourceMethodConfig.logResponse
        innerResourceInstanceMethod.enabled = resourceMethodConfig.enabled
        innerResourceInstanceMethod.muteLogs = resourceMethodConfig.muteLogs
        return innerResourceInstanceMethod
    return innerMethodWrapper


def resolveEmitterCallWithinAContext(
    args,
    kwargs,
    wrapperManager,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    responseClass,
    produces,
    httpClientResolversMap,
    returnOnlyBody,
    debugIt,
    messageCreationRequestKey,
    messageCreationRequestGroupKey,
    messageCreationRequestHeaders,
    resourceInstanceMethodMuteStacktraceOnBusinessRuleException,

    requestUrl,
    requestVerb,
    requestHeaders,
    requestParams,
    requestBody
):
    ###- https://werkzeug.palletsprojects.com/en/2.1.x/test/#werkzeug.test.EnvironBuilder
    with wrapperManager.api.app.test_request_context(
        path = requestUrl,
        method = requestVerb,
        headers = requestHeaders,
        ###- query_string = requestParams, ###- query string already comes in the url
        json = requestBody
    ):
        resolveEmitterCall(
            args,
            kwargs,
            wrapperManager,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            responseClass,
            produces,
            httpClientResolversMap,
            returnOnlyBody,
            debugIt,
            messageCreationRequestKey,
            messageCreationRequestGroupKey,
            messageCreationRequestHeaders,
            resourceInstanceMethodMuteStacktraceOnBusinessRuleException
        )


def resolveEmitterCall(
    args,
    kwargs,
    wrapperManager,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    responseClass,
    produces,
    httpClientResolversMap,
    returnOnlyBody,
    debugIt,
    messageCreationRequestKey,
    messageCreationRequestGroupKey,
    messageCreationRequestHeaders,
    resourceInstanceMethodMuteStacktraceOnBusinessRuleException
):
    resourceMethodResponse = None
    completeResponse = None
    try:
        try:
            FlaskManager.validateKwargs(
                kwargs,
                wrapperManager.resourceInstance,
                wrapperManager.resourceInstanceMethod,
                requestHeaderClass,
                requestParamClass
            )
            FlaskManager.validateArgs(args, requestClass, wrapperManager.resourceInstanceMethod)
            emitterEvent = ClientUtil.getHttpClientEvent(wrapperManager.resourceInstanceMethod, *args, **kwargs)
            if isinstance(emitterEvent, ClientUtil.ManualHttpClientEvent):
                completeResponse = emitterEvent.completeResponse
            elif isinstance(emitterEvent, ClientUtil.HttpClientEvent):
                try:
                    messageKey = messageCreationRequestKey if MessageConstant.MESSAGE_KEY_CLIENT_ATTRIBUTE_NAME not in emitterEvent.kwargs else ConverterStatic.getValueOrDefault(
                        emitterEvent.kwargs.pop(MessageConstant.MESSAGE_KEY_CLIENT_ATTRIBUTE_NAME),
                        messageCreationRequestKey
                    )
                    groupKey = messageCreationRequestGroupKey if MessageConstant.GROUP_KEY_CLIENT_ATTRIBUTE_NAME not in emitterEvent.kwargs else ConverterStatic.getValueOrDefault(
                        emitterEvent.kwargs.pop(MessageConstant.GROUP_KEY_CLIENT_ATTRIBUTE_NAME),
                        messageCreationRequestGroupKey
                    )
                    messageHeaders = messageCreationRequestHeaders if MessageConstant.MESSAGE_HEADERS_KEY_CLIENT_ATTRIBUTE_NAME not in emitterEvent.kwargs else {
                        **ConverterStatic.getValueOrDefault(emitterEvent.kwargs.pop(MessageConstant.MESSAGE_HEADERS_KEY_CLIENT_ATTRIBUTE_NAME), dict()),
                        **ConverterStatic.getValueOrDefault(messageCreationRequestHeaders, dict())
                    }
                    resourceMethodResponse = httpClientResolversMap.get(
                        emitterEvent.verb,
                        ClientUtil.raiseHttpClientEventNotFoundException
                    )(
                        wrapperManager.resourceInstance,
                        *emitterEvent.args,
                        messageKey = messageKey,
                        groupKey = groupKey,
                        messageHeaders = messageHeaders,
                        **emitterEvent.kwargs
                    )
                except Exception as exception:
                    ClientUtil.raiseException(
                        resourceMethodResponse,
                        exception,
                        context = HttpDomain.EMITTER_CONTEXT,
                        businessLogMessage = HttpEmitterConstant.ERROR_AT_CLIENT_CALL_MESSAGE,
                        defaultLogMessage = HttpEmitterConstant.CLIENT_DID_NOT_SENT_ANY_MESSAGE
                    )
                ClientUtil.raiseExceptionIfNeeded(
                    resourceMethodResponse,
                    context = HttpDomain.EMITTER_CONTEXT,
                    businessLogMessage = HttpEmitterConstant.ERROR_AT_CLIENT_CALL_MESSAGE,
                    defaultLogMessage = HttpEmitterConstant.CLIENT_DID_NOT_SENT_ANY_MESSAGE
                )
                completeResponse = ClientUtil.getCompleteResponse(resourceMethodResponse, responseClass, produces)
                FlaskManager.validateCompleteResponse(responseClass, completeResponse)
            else:
                raise Exception('Unknown emitter event')
        except Exception as exception:
            if isinstance(exception, GlobalException):
                log.log(resolveEmitterCall, 'Failure at emitter method execution', exception=exception, muteStackTrace=True)
            else:
                log.failure(resolveEmitterCall, 'Failure at emitter method execution', exception=exception)
            FlaskManager.raiseAndPersistGlobalException(
                exception,
                wrapperManager.resourceInstance,
                wrapperManager.resourceInstanceMethod,
                context = HttpDomain.EMITTER_CONTEXT
            )
    except Exception as exception:
        completeResponse = FlaskManager.getCompleteResponseByException(
            exception,
            wrapperManager.resourceInstance,
            wrapperManager.resourceInstanceMethod,
            resourceInstanceMethodMuteStacktraceOnBusinessRuleException,
            context = HttpDomain.EMITTER_CONTEXT
        )

    if wrapperManager.shouldLogResponse():
        resourceMethodResponseStatus = completeResponse[-1]
        resourceMethodResponseHeaders = completeResponse[1]
        resourceMethodResponseBody = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : HttpStatus.map(resourceMethodResponseStatus).enumName}
        log.prettyJson(
            wrapperManager.resourceInstanceMethod,
            LogConstant.EMITTER_RESPONSE,
            {
                'headers': resourceMethodResponseHeaders,
                'body': Serializer.getObjectAsDictionary(resourceMethodResponseBody, muteLogs=not debugIt),
                'status': resourceMethodResponseStatus
            },
            condition = True,
            logLevel = log.INFO
        )
    if returnOnlyBody:
        return completeResponse[0]
    else:
        return completeResponse
