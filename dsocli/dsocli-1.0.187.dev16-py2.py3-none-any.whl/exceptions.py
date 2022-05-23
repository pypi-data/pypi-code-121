class DSOException(Exception):
    
    def __init__(self, message=''):
        self.__message = message
        super().__init__(message)

    @property
    def message(self):
        return self.__message

### TODO: add DSOException descendent for every exception
