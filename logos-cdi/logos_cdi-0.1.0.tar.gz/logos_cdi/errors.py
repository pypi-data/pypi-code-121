from logos_cdi.abstract import AbstractContainer


class LogosCDIError(Exception): pass


class ResourceNotFound(LogosCDIError):

    def __init__(self, container: AbstractContainer, service_name: str):
        self.container = container
        self.service_name = service_name
        super(ResourceNotFound, self).__init__(f'service "{service_name}" not found')
