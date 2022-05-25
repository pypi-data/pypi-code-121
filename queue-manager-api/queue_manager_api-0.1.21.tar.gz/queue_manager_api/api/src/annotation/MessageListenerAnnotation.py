import json

from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework import (
    FlaskManager,
    GlobalException,
    ConverterStatic,
    FlaskUtil,
    Serializer,
    ConfigurationKeyConstant,
    EncapsulateItWithGlobalException,
    OpenApiManager,
    HttpStatus,
    HttpDomain,
    LogConstant
)

try:
    import MessageConstant
    import AnnotationUtil
    import MessageDto
except:
    from queue_manager_api.api.src.constant import MessageConstant
    from queue_manager_api.api.src.util import AnnotationUtil
    from queue_manager_api.api.src.dto import MessageDto


DEFAULT_TIMEOUT = 2


@Function
def MessageListener(
    *resourceArgs,
    url = c.SLASH,
    timeout = DEFAULT_TIMEOUT,
    responseHeaders = None,
    logRequest = False,
    logResponse = False,
    enabled = None,
    muteLogs = None,
    **resourceKwargs
):
    def Wrapper(OuterClass, *outterArgs, **outterKwargs):
        resourceUrl = url
        resourceTimeout = timeout
        resourceLogRequest = logRequest
        resourceLogResponse = logResponse
        resourceEnabled = enabled
        resourceMuteLogs = muteLogs
        resourceInstanceResponseHeaders = responseHeaders
        log.wrapper(MessageListener, f'''wrapping {OuterClass.__name__}(*{outterArgs}, **{outterKwargs})''')
        api = FlaskManager.getApi()
        class InnerClass(OuterClass):
            url = resourceUrl
            responseHeaders = resourceInstanceResponseHeaders
            logRequest = resourceLogRequest
            logResponse = resourceLogResponse
            enabled = resourceEnabled
            muteLogs = resourceMuteLogs
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
                    resourceEnabledConfigKey = ConfigurationKeyConstant.API_LISTENER_ENABLE,
                    resourceMuteLogsConfigKey = ConfigurationKeyConstant.API_LISTENER_MUTE_LOGS,
                    resourceTimeoutConfigKey = ConfigurationKeyConstant.API_LISTENER_TIMEOUT
                )
                self.queueManager = api.queueManager
        ReflectionHelper.overrideSignatures(InnerClass, OuterClass)
        return InnerClass
    return Wrapper


@Function
def MessageListenerMethod(
    *methodArgs,
    url = c.SLASH,
    timeout = DEFAULT_TIMEOUT,
    requestHeaderClass = None,
    requestParamClass = None,
    requestClass = None,
    responseClass = None,
    responseHeaders = None,
    roleRequired = None,
    apiKeyRequired = None,
    contextRequired = None,
    consumes = OpenApiManager.DEFAULT_CONTENT_TYPE,
    produces = OpenApiManager.DEFAULT_CONTENT_TYPE,
    logRequest = True,
    logResponse = True,
    enabled = True,
    muteLogs = False,
    muteStacktraceOnBusinessRuleException = True,
    runInAThread = False,
    **methodKwargs
):
    def innerMethodWrapper(resourceInstanceMethod, *innerMethodArgs, **innerMethodKwargs):
        resourceInstanceMethodUrl = url
        wrapperManager = AnnotationUtil.InnerMethodWrapperManager(
            wrapperType = MessageListenerMethod,
            resourceInstanceMethod = resourceInstanceMethod,
            timeout = timeout,
            enabled = enabled,
            muteLogs = muteLogs,
            logRequest = logRequest,
            logResponse = logResponse,
            resourceTypeName = FlaskManager.KW_LISTENER_RESOURCE,
            resourceEnabledConfigKey = ConfigurationKeyConstant.API_LISTENER_ENABLE,
            resourceMuteLogsConfigKey = ConfigurationKeyConstant.API_LISTENER_MUTE_LOGS,
            resourceTimeoutConfigKey = ConfigurationKeyConstant.API_LISTENER_TIMEOUT
        )
        resourceInstanceMethodMuteStacktraceOnBusinessRuleException = muteStacktraceOnBusinessRuleException
        resourceInstanceMethodRunInAThread = runInAThread
        listenerUrl = f'{wrapperManager.api.baseUrl}{resourceInstanceMethodUrl}'
        if listenerUrl.endswith(c.SLASH):
            listenerUrl = listenerUrl[:-1]
        @wrapperManager.api.app.route(listenerUrl, methods=[HttpDomain.Verb.POST], endpoint=f'{resourceInstanceMethod.__qualname__}')
        def innerResourceInstanceMethod(*args, **kwargs):
            args = wrapperManager.addResourceInFrontOfArgs(args)
            messageAsJson = FlaskUtil.safellyGetRequestBody()
            completeResponse = None
            if not wrapperManager.muteLogs:
                requestUrl = FlaskUtil.safellyGetUrl()
                requestVerb = FlaskUtil.safellyGetVerb()
                log.info(wrapperManager.resourceInstanceMethod, f'''{LogConstant.LISTENER_SPACE}{requestVerb}{c.SPACE_DASH_SPACE}{requestUrl}''')
                try:
                    messageCreationRequestDto = Serializer.getObjectAsDictionary(Serializer.convertFromJsonToObject(messageAsJson, MessageDto.MessageCreationRequestDto))
                    log.prettyPython(wrapperManager.resourceInstanceMethod, f'{LogConstant.LISTENER_SPACE}Message data', messageCreationRequestDto, logLevel=log.INFO)
                except Exception as exception:
                    log.failure(innerResourceInstanceMethod, 'Not possible to log message data properly', exception)
            if not wrapperManager.enabled:
                completeResponse = FlaskManager.getCompleteResponseByException(
                    GlobalException(logMessage='This resource is temporarily disabled', status=HttpStatus.SERVICE_UNAVAILABLE),
                    wrapperManager.resourceInstance,
                    wrapperManager.resourceInstanceMethod,
                    resourceInstanceMethodMuteStacktraceOnBusinessRuleException,
                    context = HttpDomain.LISTENER_CONTEXT
                )
            elif ObjectHelper.isEmpty(messageAsJson):
                completeResponse = FlaskManager.getCompleteResponseByException(
                    GlobalException(message='Content cannot be empty', logResponse=f'Content: {messageContent}', status=HttpStatus.BAD_REQUEST),
                    wrapperManager.resourceInstance,
                    wrapperManager.resourceInstanceMethod,
                    resourceInstanceMethodMuteStacktraceOnBusinessRuleException,
                    context = HttpDomain.LISTENER_CONTEXT
                )
            else:
                listennerArgs = (
                    args,
                    kwargs,
                    wrapperManager,
                    roleRequired,
                    apiKeyRequired,
                    contextRequired,
                    requestHeaderClass,
                    requestParamClass,
                    requestClass,
                    responseClass,
                    responseHeaders,
                    consumes,
                    resourceInstanceMethodMuteStacktraceOnBusinessRuleException,

                    requestUrl,
                    requestVerb,
                    FlaskUtil.safellyGetHeaders(),
                    FlaskUtil.safellyGetArgs(),
                    messageAsJson.get(MessageConstant.MESSAGE_CONTENT_KEY, {})
                )
                if resourceInstanceMethodRunInAThread:
                    wrapperManager.resourceInstance.queueManager.runInAThread(resolveListenerCallWithinAContext, *listennerArgs)
                else:
                    completeResponse = resolveListenerCall(*listennerArgs)
                if ObjectHelper.isEmpty(completeResponse) or HttpStatus.BAD_REQUEST < completeResponse[-1]:
                    completeResponse = [
                        MessageDto.MessageCreationResponseDto(
                            key = messageAsJson.get(MessageConstant.MESSAGE_KEY_KEY),
                            queueKey = messageAsJson.get(MessageConstant.MESSAGE_QUEUE_KEY_KEY),
                            groupKey = messageAsJson.get(MessageConstant.MESSAGE_GROUP_KEY)
                        ),
                        {},
                        HttpStatus.ACCEPTED
                    ]
            httpResponse = FlaskUtil.buildHttpResponse(completeResponse[1], completeResponse[0], completeResponse[-1].enumValue, produces)
            if wrapperManager.shouldLogResponse():
                try:
                    resourceMethodResponseStatus = completeResponse[-1]
                    log.prettyJson(
                        wrapperManager.resourceInstanceMethod,
                        LogConstant.LISTENER_RESPONSE,
                        {
                            'headers': FlaskUtil.safellyGetResponseHeaders(httpResponse),
                            'body': FlaskUtil.safellyGetFlaskResponseJson(httpResponse),
                            'status': resourceMethodResponseStatus.enumValue
                        },
                        condition = True,
                        logLevel = log.INFO
                    )
                except Exception as exception:
                    log.failure(innerResourceInstanceMethod, 'Not possible to log response properly', exception)

            return httpResponse
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, wrapperManager.resourceInstanceMethod)
        innerResourceInstanceMethod.url = url
        innerResourceInstanceMethod.requestHeaderClass = requestHeaderClass
        innerResourceInstanceMethod.requestParamClass = requestParamClass
        innerResourceInstanceMethod.requestClass = requestClass
        innerResourceInstanceMethod.responseClass = responseClass
        innerResourceInstanceMethod.responseHeaders = responseHeaders
        innerResourceInstanceMethod.apiKeyRequired = apiKeyRequired
        innerResourceInstanceMethod.produces = produces
        innerResourceInstanceMethod.consumes = consumes
        innerResourceInstanceMethod.logRequest = logRequest
        innerResourceInstanceMethod.logResponse = logResponse
        innerResourceInstanceMethod.enabled = enabled
        innerResourceInstanceMethod.muteLogs = muteLogs
        innerResourceInstanceMethod.muteStacktraceOnBusinessRuleException = resourceInstanceMethodMuteStacktraceOnBusinessRuleException
        innerResourceInstanceMethod.runInAThread = resourceInstanceMethodRunInAThread
        return innerResourceInstanceMethod
    return innerMethodWrapper


def resolveListenerCallWithinAContext(
    args,
    kwargs,
    wrapperManager,
    roleRequired,
    apiKeyRequired,
    contextRequired,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    responseClass,
    defaultResponseHeaders,
    consumes,
    resourceInstanceMethodMuteStacktraceOnBusinessRuleException,

    requestUrl,
    requestVerb,
    requestHeaders,
    requestParams,
    requestBody,

    logRequestMessage = LogConstant.LISTENER_REQUEST,
    context = HttpDomain.LISTENER_CONTEXT
):
    ###- https://werkzeug.palletsprojects.com/en/2.1.x/test/#werkzeug.test.EnvironBuilder
    with wrapperManager.api.app.test_request_context(
        path = requestUrl,
        method = requestVerb,
        headers = requestHeaders,
        ###- query_string = requestParams, ###- query string already comes in the url
        json = requestBody
    ):
        resolveListenerCall(
            args,
            kwargs,
            wrapperManager,
            roleRequired,
            apiKeyRequired,
            contextRequired,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            responseClass,
            defaultResponseHeaders,
            consumes,
            resourceInstanceMethodMuteStacktraceOnBusinessRuleException,

            requestUrl,
            requestVerb,
            requestHeaders,
            requestParams,
            requestBody,

            logRequestMessage = LogConstant.LISTENER_REQUEST,
            context = HttpDomain.LISTENER_CONTEXT
        )



def resolveListenerCall(
    args,
    kwargs,
    wrapperManager,
    roleRequired,
    apiKeyRequired,
    contextRequired,
    requestHeaderClass,
    requestParamClass,
    requestClass,
    responseClass,
    defaultResponseHeaders,
    consumes,
    resourceInstanceMethodMuteStacktraceOnBusinessRuleException,

    requestUrl,
    requestVerb,
    requestHeaders,
    requestParams,
    requestBody,

    logRequestMessage = LogConstant.LISTENER_REQUEST,
    context = HttpDomain.LISTENER_CONTEXT
):
    completeResponse = None
    try:
        completeResponse = FlaskManager.handleAnyControllerMethodRequest(
            args,
            kwargs,
            consumes,
            wrapperManager.resourceInstance,
            wrapperManager.resourceInstanceMethod,
            contextRequired,
            apiKeyRequired,
            roleRequired,
            requestHeaderClass,
            requestParamClass,
            requestClass,
            wrapperManager.shouldLogRequest(),
            resourceInstanceMethodMuteStacktraceOnBusinessRuleException,
            verb = requestVerb,
            requestHeaders = requestHeaders,
            requestParams = requestParams,
            requestBody = requestBody,
            logRequestMessage = logRequestMessage
        )
        FlaskManager.validateCompleteResponse(responseClass, completeResponse)
    except Exception as exception:
        log.log(resolveListenerCall, 'Failure at controller method execution. Getting complete response as exception', exception=exception, muteStackTrace=True)
        completeResponse = FlaskManager.getCompleteResponseByException(
            exception,
            wrapperManager.resourceInstance,
            wrapperManager.resourceInstanceMethod,
            resourceInstanceMethodMuteStacktraceOnBusinessRuleException,
            context = context
        )
    try:
        status = HttpStatus.map(completeResponse[-1])
        additionalResponseHeaders = completeResponse[1]
        if ObjectHelper.isNotNone(wrapperManager.resourceInstance.responseHeaders):
            additionalResponseHeaders = {**wrapperManager.resourceInstance.responseHeaders, **additionalResponseHeaders}
        if ObjectHelper.isNotNone(defaultResponseHeaders):
            additionalResponseHeaders = {**defaultResponseHeaders, **additionalResponseHeaders}
        responseBody = completeResponse[0] if ObjectHelper.isNotNone(completeResponse[0]) else {'message' : status.enumName}
        completeResponse = [responseBody, additionalResponseHeaders, status]
    except Exception as exception:
        log.failure(resolveListenerCall, f'Failure while parsing complete response: {completeResponse}. Returning simplified version of it', exception, muteStackTrace=True)
        completeResponse = getCompleteResponseByException(
            Exception(f'Not possible to handle complete response{c.DOT_SPACE_CAUSE}{str(exception)}'),
            wrapperManager.resourceInstance,
            wrapperManager.resourceInstanceMethod,
            resourceInstanceMethodMuteStacktraceOnBusinessRuleException
        )
    return completeResponse
