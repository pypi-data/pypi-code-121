__author__ = 'Andres Alvarado'


class CFDIException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

    def __unicode__(self):
        return repr(self.message)


class ServiceFacturaException(Exception):

    def __init__(self, e, provider, service, status = 0, message = 'Error', typeError = 'Exception'):
        self.provider = provider
        self.service = service
        self.status = status
        self.message = message
        self.typeError = typeError
        if e is not None:
            if type(e) == str:
                self.message = e
            elif e.__class__:
                if e.__class__.__name__:
                    name = e.__class__.__name__
                    message = str(e)
                    self.typeError = name
                    self.message = message
                    if name == 'ConnectTimeout':  # Tipo de error por conexion tardia
                        self.message = message
                        self.status = 408
                    elif name == 'timeout':
                        self.status = 408
                    elif name == 'HTTPError':  # Tipo de error http (ej: 401, 500)
                        self.status = e.response.status_code
                    elif name == 'Fault':  # Tipo de error regresado por el servicio
                        self.status = 200
                    elif name == 'ServiceFacturaException':
                        self.provider = e.provider
                        self.service = e.service
                        self.status = e.status
                        self.message = message
                        self.typeError = e.typeError

    def __str__(self):
        message = self.message
        if type(message) == str:
            message = message.encode('utf-8').decode()
        return message


class WebServiceException(Exception):

    def __init__(self, message, status):
        self.message = message
        self.status = status

    def __str__(self):
        return repr(self.message)

    def __unicode__(self):
        return repr(self.message)
