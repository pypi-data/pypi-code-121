from python_framework import Serializer, HttpStatus, JwtConstant
from MessageEmitterAnnotation import MessageEmitter
from MessageEmitterAnnotation import MessageEmitterMethod

from config import MessageConfig
import MessageDto
import Message


@MessageEmitter(
    url = MessageConfig.EMITTER_URL,
    timeout = MessageConfig.EMITTER_TIMEOUT,
    headers = {
        'Content-Type': 'application/json',
        JwtConstant.DEFAULT_JWT_API_KEY_HEADER_NAME: f'Bearer {MessageConfig.MESSAGE_API_KEY}'
    }
    , muteLogs = False
    , logRequest = True
    , logResponse = True
)
class MessageEmitter:

    @MessageEmitterMethod(
        queueKey = MessageConfig.SOME_UNIQUE_QUEUE_KEY,
        requestClass=[MessageDto.MessageRequestDto],
        responseClass=[MessageDto.MessageRequestDto]
        , logRequest = True
        , logResponse = True
    )
    def send(self, dto):
        return self.emit(body=dto)
