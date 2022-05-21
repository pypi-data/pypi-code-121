class RequestHandler:
    def __init__(self, request: str):
        """
        :param request: msg.decode('utf-8').split('\r\n')[0]
        """
        self._method = request.split()
