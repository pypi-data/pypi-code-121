from python_framework import Controller, ControllerMethod, HttpStatus

from enumeration.AccessDomain import AccessDomain
import QueueDto


@Controller(url = '/queue', tag='Queue', description='Queue controller')
class QueueModelController:

    @ControllerMethod(url = '/',
        apiKeyRequired = [AccessDomain.API],
        requestClass = [QueueDto.QueueRequestDto],
        responseClass = [QueueDto.QueueResponseDto]
        # , logRequest = True
        # , logResponse = True
    )
    def post(self, dto):
        return self.service.queueModel.createOrUpdate(dto), HttpStatus.CREATED


@Controller(url = '/queue/all', tag='Queue', description='Queue controller')
class QueueModelAllController:

    @ControllerMethod(url = '/',
        apiKeyRequired = [AccessDomain.API],
        responseClass = [[QueueDto.QueueResponseDto]]
        # , logRequest = True
        # , logResponse = True
    )
    def get(self):
        return self.service.queueModel.findAllByOrigin(), HttpStatus.OK
