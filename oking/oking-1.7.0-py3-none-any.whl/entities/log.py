
class Log:
    def __init__(self, error: str, date_time: str, identifier: str, method: str):
        self.erro: str = error[0:2000] if error is not None else ''
        self.data_hora: str = date_time
        self.identificador: str = identifier
        self.metodo: str = method
