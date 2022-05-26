import sys


class AlreadyInitialized(Exception):
    pass


class InvalidProjectName(Exception):
    pass


class ProjectNotInitialized(Exception):
    pass


class CredentialsNotFound(Exception):
    pass


class InvalidOrgName(Exception):
    pass


class MalformedKeys(Exception):
    pass


class KeysMixedUp(Exception):
    pass


class InvalidUrl(Exception):
    pass


class LoginFailed(Exception):
    pass


class ModelNotFound(Exception):
    def __init__(self):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()


class MappingNotFound(Exception):
    def __init__(self):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()


class ParseDatasetFailed(Exception):
    def __init__(self):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()


class ModelEntryPointNotFound(Exception):
    def __init__(self):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()


class ModelSaveFailure(Exception):
    def __init__(self):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()


class DoctorCheckFailed(Exception):
    def __init__(self):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()


class ProjectNotFoundException(Exception):
    def __init__(self, project_name):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()
        self.project_name = project_name


class SecretNotFoundException(Exception):
    def __init__(self, secret_name):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()
        self.secret_name = secret_name


class DatasetNotFoundException(Exception):
    def __init__(self, dataset_name):
        super().__init__()
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()
        self.dataset_name = dataset_name


class DatabaseAmbiguityException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.exc_type, self.inner_exception, self.traceback = sys.exc_info()


class ModelNotSaved(Exception):
    pass
