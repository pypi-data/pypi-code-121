from python_framework import Controller, ControllerMethod, HttpStatus, ConverterStatic

from enumeration.AccessDomain import AccessDomain
import MessageDto


@Controller(url = '/test/message', tag='QueueTest', description='Queue test controller')
class MessateTestController:


    @ControllerMethod(url = '/',
        apiKeyRequired = ['SOMETHING_ELSE'],
        requestClass = [MessageDto.MessageRequestDto],
        responseClass = [MessageDto.MessageResponseDto]
        , logRequest = True
        , logResponse = True
    )
    def post(self, dto):
        return ConverterStatic.to(dto, MessageDto.MessageResponseDto), HttpStatus.OK


@Controller(url = '/test/message-error', tag='QueueTest', description='Queue test controller')
class MessateTestBulkController:

    @ControllerMethod(url = '/',
        apiKeyRequired = [AccessDomain.API],
        requestClass = [MessageDto.MessageRequestDto],
        responseClass = [MessageDto.MessageResponseDto]
        , logRequest = True
        , logResponse = True
    )
    def post(self, dto):
        return ConverterStatic.to(dto, MessageDto.MessageResponseDto), HttpStatus.OK
