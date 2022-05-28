import sys


__all__ = ['nullcontext']


if sys.version_info >= (3, 10):
    from contextlib import (
        nullcontext,
    )
else:
    from contextlib import (
        AbstractAsyncContextManager,
        AbstractContextManager,
    )

    class nullcontext(AbstractContextManager, AbstractAsyncContextManager):
        """
        Бэкпорт contextlib.nullcontext из Python 3.10+
        """

        def __init__(self, enter_result=None):
            self.enter_result = enter_result

        def __enter__(self):
            return self.enter_result

        def __exit__(self, *excinfo):
            pass

        async def __aenter__(self):
            return self.enter_result

        async def __aexit__(self, *excinfo):
            pass
