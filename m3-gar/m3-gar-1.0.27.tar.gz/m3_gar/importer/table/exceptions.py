from m3_gar.importer.exceptions import (
    ImporterError,
)


class BadTableError(ImporterError):
    pass


class ParentLookupError(ImporterError):
    pass
