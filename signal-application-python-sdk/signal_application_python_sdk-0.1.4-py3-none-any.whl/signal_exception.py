SDK_INIT_ERROR = 'signalsdk::Please initialize Signal Application SDK first!'
SDK_APP_CONFIG_ENV_ERROR = 'signalsdk::Check deployment environment!'
SDK_APP_ID_NOT_FOUND_ERROR = 'signalsdk::Application Id not found on environment!'
SDK_APP_PARAM_NOT_FOUND_ERROR = "signalsdk::Parameter not found"
SDK_APP_CALL_BACK_ERROR = "signalsdk::config change cb function threw an error"
SDK_APP_IOT_CONN_ERROR = "signalsdk::IoT MQTT connection error"
SDK_APP_SIGNED_REQ_ERROR = "signalsdk:signed request error"
SDK_DEPLOYMENT_ID_NOT_FOUND_ERROR = ('signalsdk:deploymentId  or groupDeploymentId '
                                     'not found on config error')
SDK_DEVICE_DOMAIN_NOT_FOUND_ERROR = "signalsdk:device api domain not found on config error"


class SignalAppInitError(Exception):
    def __str__(self):
        return SDK_INIT_ERROR


class SignalAppConfigEnvError(Exception):
    def __str__(self):
        return SDK_APP_ID_NOT_FOUND_ERROR


class SignalDeploymentNotFoundError(Exception):
    def __str__(self):
        return SDK_DEPLOYMENT_ID_NOT_FOUND_ERROR


class SignalDeviceDomainNotFoundError(Exception):
    def __str__(self):
        return SDK_DEVICE_DOMAIN_NOT_FOUND_ERROR


class SignalAppParamNotFoundError(Exception):
    def __str__(self):
        return SDK_APP_PARAM_NOT_FOUND_ERROR


class SignalAppCallBackError(Exception):
    def __str__(self):
        return SDK_APP_CALL_BACK_ERROR


class SignalAppIoTConError(Exception):
    def __str__(self):
        return SDK_APP_IOT_CONN_ERROR


class SignalAppSignedReqError(Exception):
    def __str__(self):
        return SDK_APP_SIGNED_REQ_ERROR
