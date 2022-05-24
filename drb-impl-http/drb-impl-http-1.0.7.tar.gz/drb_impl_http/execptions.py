from drb.exceptions import DrbException, DrbFactoryException


class DrbHttpNodeException(DrbException):
    pass


class DrbHttpAuthException(DrbException):
    pass


class DrbHttpServerException(DrbException):
    pass


class DrbHttpNodeFactoryException(DrbFactoryException):
    pass
