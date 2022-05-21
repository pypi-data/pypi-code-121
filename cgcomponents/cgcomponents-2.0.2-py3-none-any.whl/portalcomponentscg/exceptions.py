from logs import LogsCriticalErros, LogsErros


class CGExceptionsErros(Exception):
    """Base class for CG exceptions"""
    pass


class CGExceptionsRDS(IOError):
    """Base class for RDS exceptions"""
    pass


class CGExceptionsRequestsErros(IOError):
    """Base class for requestsCG exceptions"""
    pass


""" Generic Exceptions """


class ErrorJson(CGExceptionsRequestsErros):

    def __init__(self, component, message="JSON Tratase de um DataSet, por gentileza utilize json.dumps(json)"):
        self.component = component
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        LogsErros([self.component, self.message])
        return f'{self.component} -> {self.message}'


class ErrorCredentials(CGExceptionsErros):

    def __init__(self, component, message="Credenciais de Login incorretas. Por gentileza verifique-as"):
        self.component = component
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        LogsErros([self.component, self.message])
        return f'{self.component} -> {self.message}'


""" BackEnd Exceptions """


class BackEndConnectionError(CGExceptionsRequestsErros):
    def __init__(self, suggestion="Inicie o Serviço do BackEnd", message="Falha ao conectar-se ao servidor Django"):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message, suggestion)

    def __str__(self):
        LogsCriticalErros(self.message)
        return f'{self.suggestion} -> {self.message}'


""" INTRANET EXCEPTIONS """


class IntranetConnectionError(CGExceptionsRequestsErros):
    def __init__(self, suggestion="Conect-se ao FortClient", message="Falha ao conectar-se com o Intranet"):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message, suggestion)

    def __str__(self):
        LogsCriticalErros(self.message)

        return f'{self.suggestion} -> {self.message}'


""" RDS EXCEPTIONS """


class ErrorConnectionRDS(CGExceptionsRDS):

    def __init__(self, component, message="Erro ao tentar conectar-se ao banco RDS"):
        self.component = component
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        LogsCriticalErros([self.component, self.message])

        return f'{self.component} -> {self.message}'
