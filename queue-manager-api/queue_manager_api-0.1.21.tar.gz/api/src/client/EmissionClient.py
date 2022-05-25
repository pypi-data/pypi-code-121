from python_framework import Serializer, HttpStatus, HttpClient, HttpClientMethod

from config import MessageConfig
import MessageDto
import Emission


@HttpClient(
    logRequest = True,
    logResponse = True,
    timeout = MessageConfig.EMITTER_TIMEOUT,
    headers = {'Content-Type': 'application/json'}
)
class EmissionClient:

    @HttpClientMethod(
        logRequest = True,
        logResponse = True,
        requestHeaderClass = dict,
        requestClass = [str, MessageDto.MessageRequestDto],
        responseClass = [MessageDto.MessageCreationResponseDto]
    )
    def send(self, url, dto, headers=None):
        return self.post(
            additionalUrl = url,
            headers = headers,
            body = Serializer.getObjectAsDictionary(dto)
        )
