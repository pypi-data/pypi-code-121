class ERPException(Exception):
    mope_code: str
    message: str

    def __init__(self, mope_code: str, message: str):
        super().__init__(f'{mope_code} - {message}')
        self.mope_code = mope_code
        self.message = message


class PaginationException(ERPException):
    def __init__(self, msg: str):
        super().__init__('0000-E001',
                         f'Erro nos parâmetros requisitados para paginação: {msg}')


class NotFoundException(Exception):
    pass
