class InvalidTransactionHashError(Exception):
    pass


class TransactionParsingError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class APIError(Exception):
    pass


class InvalidAccountError(Exception):
    pass


class AccountParsingError(Exception):
    pass


class InvalidQueryError(Exception):
    pass


class TransactionSimulationError(Exception):
    pass
