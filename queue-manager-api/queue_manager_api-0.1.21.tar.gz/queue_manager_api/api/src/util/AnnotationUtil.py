from python_helper import Constant as c
from python_helper import ReflectionHelper, ObjectHelper, log, Function, StringHelper
from python_framework import (
    FlaskManager,
    ConverterStatic,
    Listener,
    ListenerMethod,
    FlaskUtil,
    Serializer
)


DEFAUTL_RESOURCE_ENABLED = False
DEFAUTL_RESOURCE_MUTE_LOGS = False
DEFAUTL_RESOURCE_METHOD_ENABLED = True
DEFAUTL_RESOURCE_METHOD_MUTE_LOGS = False
DEFAULT_TIMEOUT = 30


def initializeComunicationLayerResource(
    resourceInstance = None,
    api = None,
    enabled = None,
    muteLogs = None,
    logRequest = False,
    logResponse = False,
    timeout = None,
    resourceEnabledConfigKey = None,
    resourceMuteLogsConfigKey = None,
    resourceTimeoutConfigKey = None,
    defaultEnabled = DEFAUTL_RESOURCE_ENABLED,
    defaultMuteLogs = DEFAUTL_RESOURCE_MUTE_LOGS,
    defaultTimeout = DEFAULT_TIMEOUT
):
    api = FlaskUtil.retrieveApiInstance(apiInstance=api, arguments=(resourceInstance,))
    resourceInstance.enabled = enabled and ConverterStatic.getValueOrDefault(
        api.globals.getApiSetting(resourceEnabledConfigKey),
        defaultEnabled
    )
    resourceInstance.muteLogs = muteLogs or ConverterStatic.getValueOrDefault(
        api.globals.getApiSetting(resourceMuteLogsConfigKey),
        defaultMuteLogs
    )
    resourceInstance.timeout = ConverterStatic.getValueOrDefault(
        timeout,
        ConverterStatic.getValueOrDefault(
            api.globals.getApiSetting(resourceTimeoutConfigKey),
            defaultTimeout
        )
    )
    resourceInstance.logRequest = logRequest
    resourceInstance.logResponse = logResponse
    resourceInstance.globals = api.globals
    resourceInstance.service = api.resource.service
    resourceInstance.defaultEnabled = defaultEnabled
    resourceInstance.defaultMuteLogs = defaultMuteLogs
    resourceInstance.defaultTimeout = defaultTimeout


class InnerMethodWrapperManager:

    def __init__(
        self,
        resourceInstanceMethodArguments = None,
        wrapperType = None,
        resourceInstanceMethod = None,
        timeout = None,
        enabled = None,
        muteLogs = None,
        resourceEnabled = None,
        resourceMuteLogs = None,
        logRequest = False,
        logResponse = False,
        resourceTypeName = None,
        resourceEnabledConfigKey = None,
        resourceMuteLogsConfigKey = None,
        resourceTimeoutConfigKey = None,
        defaultEnabled = DEFAUTL_RESOURCE_METHOD_ENABLED,
        defaultMuteLogs = DEFAUTL_RESOURCE_METHOD_MUTE_LOGS,
        defaultTimeout = DEFAULT_TIMEOUT,
        **methodKwargs
    ):
        log.wrapper(wrapperType, f'''wrapping {resourceInstanceMethod.__name__}''')
        self.api = FlaskManager.getApi()

        self.resourceInstance = None
        self.resourceInstanceMethod = resourceInstanceMethod
        self.resourceTypeName = resourceTypeName
        self.methodClassName = ReflectionHelper.getMethodClassName(self.resourceInstanceMethod)
        self.methodName = ReflectionHelper.getName(self.resourceInstanceMethod)
        resourceInstanceName = self.methodClassName[:-len(self.resourceTypeName)]
        self.resourceInstanceName = f'{resourceInstanceName[0].lower()}{resourceInstanceName[1:]}'
        self.id = methodKwargs.get('id', f'{self.methodClassName}{c.DOT}{self.methodName}')
        self.defaultEnabled = defaultEnabled
        self.defaultMuteLogs = defaultMuteLogs
        self.defaultTimeout = defaultTimeout
        self.enabled = enabled and ConverterStatic.getValueOrDefault(
            self.api.globals.getApiSetting(resourceEnabledConfigKey),
            self.defaultEnabled
        )
        self.muteLogs = muteLogs or ConverterStatic.getValueOrDefault(
            self.api.globals.getApiSetting(resourceMuteLogsConfigKey),
            self.defaultMuteLogs
        )
        self.timeout = ConverterStatic.getValueOrDefault(
            timeout,
            ConverterStatic.getValueOrDefault(
                self.api.globals.getApiSetting(resourceTimeoutConfigKey),
                self.defaultTimeout
            )
        )
        self.logRequest = logRequest
        self.logResponse = logResponse
        self.resourceInstance = self.updateResourceInstance(ConverterStatic.getValueOrDefault(resourceInstanceMethodArguments, list()))


    def shouldLogRequest(self):
        return self.resourceInstance.logRequest and self.logRequest


    def shouldLogResponse(self):
        return self.resourceInstance.logResponse and self.logResponse


    def updateResourceInstance(self, args):
        if ObjectHelper.isNone(self.resourceInstance):
            if ObjectHelper.isNone(args) or ObjectHelper.isEmpty(args):
                try:
                    self.resourceInstance = FlaskManager.getResourceSelf(
                        self.api,
                        self.resourceTypeName,
                        self.resourceInstanceName
                    )
                except Exception as exception:
                    log.log(self.updateResourceInstance, f'Not possible to get "{self.resourceInstanceName}" resource instance. Make sure to add it in method usage scope', exception=exception, muteStackTrace=True)
            else :
                self.resourceInstance = args[0]
        try :
            resourceInstanceEnabled = ConverterStatic.getValueOrDefault(self.resourceInstance.enabled, self.defaultEnabled)
            resourceInstanceMuteLogs = ConverterStatic.getValueOrDefault(self.resourceInstance.muteLogs, self.defaultMuteLogs)
            self.timeout = ConverterStatic.getValueOrDefault(self.timeout, ConverterStatic.getValueOrDefault(self.resourceInstance.timeout, self.defaultTimeout))
            self.enabled = resourceInstanceEnabled and ConverterStatic.getValueOrDefault(self.enabled, self.defaultEnabled)
            self.muteLogs = resourceInstanceMuteLogs or ConverterStatic.getValueOrDefault(self.muteLogs, self.defaultMuteLogs)
            self.logRequest = self.logRequest and ConverterStatic.getValueOrDefault(self.resourceInstance.logRequest, False)
            self.logResponse = self.logResponse and ConverterStatic.getValueOrDefault(self.resourceInstance.logResponse, False)
        except Exception as exception:
            log.log(self.updateResourceInstance, f'Not possible to update "{self.resourceInstanceName}" resource instance configurations properly. Make sure to do it within method usage scope', exception=exception, muteStackTrace=True)
        return self.resourceInstance


    def addResourceInFrontOfArgs(self, args):
        return FlaskManager.getArgumentInFrontOfArgs(args, self.updateResourceInstance(tuple()))
