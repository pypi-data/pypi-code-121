class Error(Exception):
    """Main error class to be inherited in all app's custom errors."""
    def __init__(self, message: str = '', status_code: int = 400) -> None:
        super().__init__(message)
        if type(message) is str:
            self.message: str = message
        else:
            raise TypeError(
                'Error first argument (message) should be str,'
                f' got {type(message)} instead')
        if type(status_code) is int:
            self.status_code: int = status_code
        else:
            raise TypeError(
                'Error second argument (status_code) should be int,'
                f' got {type(status_code)} instead')

    def expose(self) -> dict:
        return {"error": {
            "name": self.__class__.__name__,
            "message": "; ".join(self.args),
            "status_code": self.status_code
        }}
