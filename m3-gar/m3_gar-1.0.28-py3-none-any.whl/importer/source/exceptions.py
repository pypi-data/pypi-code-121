from m3_gar.importer.exceptions import (
    ImporterError,
)


class TableListLoadingError(ImporterError):
    pass


class NoNewVersionError(ImporterError):
    pass


class BadArchiveError(TableListLoadingError):

    def __init__(self, source, *args):
        super().__init__(
            f'Archive: `{source}` corrupted or is not archive',
            *args,
        )


class EmptyArchiveError(TableListLoadingError):
    def __init__(self, source, *args):
        super().__init__(
            f'Archive: `{source}` is empty',
            *args
        )


class RetrieveError(TableListLoadingError):
    pass
