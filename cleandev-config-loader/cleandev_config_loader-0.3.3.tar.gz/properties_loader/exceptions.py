from properties_loader.inmutables import _MsgError


class PropertiesNotFoundError(Exception):
    def __init__(self, root_path: str, message: str = str(_MsgError.ERROR_TO_LOAD_PROPERTIES_FILE)):
        super(PropertiesNotFoundError, self).__init__(f'{message} -> {root_path}')
