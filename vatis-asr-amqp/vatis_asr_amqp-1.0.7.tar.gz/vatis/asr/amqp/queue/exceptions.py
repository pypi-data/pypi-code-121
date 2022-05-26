from typing import Type, Optional


class ConnectionClosedException(Exception):
    pass


class RetriesExceededException(Exception):
    pass


class NoRouteFoundException(Exception):
    pass


class NoConsumerException(Exception):
    def __init__(self, message_type: Optional[Type]):
        super().__init__(f'Message type: {str(message_type)}')
        self.message_type: Type = message_type


class UnknownBodyTypeException(Exception):
    pass


class CorruptedBodyException(Exception):
    pass
