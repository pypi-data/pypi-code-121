from python_helper import log
from python_framework import HttpStatus, FlaskUtil

from annotation.MessageListenerAnnotation import MessageListener
from annotation.MessageListenerAnnotation import MessageListenerMethod

from enumeration.AccessDomain import AccessDomain
from config import MessageConfig
import MessageDto
import Message


@MessageListener(
    timeout = MessageConfig.LISTENER_TIMEOUT
    , logRequest = True
    , logResponse = True
    , muteLogs = False
)
class MessageListener:

    @MessageListenerMethod(url = '/test/listener/message',
        requestClass=[MessageDto.MessageRequestDto],
        responseClass=[MessageDto.MessageCreationRequestDto],
        apiKeyRequired=[AccessDomain.API]
        , logRequest = True
        , logResponse = True
    )
    def accept(self, dto):
        return self.service.message.globals.api.resource.emitter.message.send(dto), HttpStatus.ACCEPTED


    @MessageListenerMethod(url = '/test/listener/another-message',
        requestClass=[MessageDto.MessageRequestDto],
        responseClass=[MessageDto.MessageCreationRequestDto],
        apiKeyRequired=[AccessDomain.API]
        , logRequest = True
        , logResponse = True
    )
    def anotherAccept(self, dto):
        return self.service.message.globals.api.resource.emitter.message.send(dto), HttpStatus.ACCEPTED
