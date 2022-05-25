from python_framework import Controller, ControllerMethod, HttpStatus

from enumeration.AccessDomain import AccessDomain


@Controller(url = '/memory', tag='Memory', description='Memory controller')
class MemoryController:

    @ControllerMethod(url = '/',
        apiKeyRequired = [AccessDomain.ADMIN]
        # requestClass = [MessageDto.MessageRequestDto]
        # responseClass = [MessageDto.MessageResponseDto]
        # responseClass = [MessageDto.MessageRequestDto]
        # , logRequest = True
        # , logResponse = True
    )
    def get(self):
        return self.service.memory.findAll(), HttpStatus.OK
