from collections.abc import Mapping as _Mapping
from contextlib import ExitStack
from copy import copy
from typing import Any, Optional, Mapping, Dict

import teradatasql
from pandakeeper.dataloader.sql import SqlLoader
from pandakeeper.validators import AnyDataFrame
from pandera import DataFrameSchema
from typing_extensions import final
from varutils.typing import check_type_compatibility

from sber_ld_dbtools.credentials import PasswordKeeper
from sber_ld_dbtools.loader.config import GlobalConfigType

__all__ = (
    'TeradataContextManager',
    'TeradataLoader',
    'GlobalTeradataConfig'
)


class TeradataContextManager:
    __slots__ = ('host', 'user', '__password', 'logmech', 'connection')

    def __init__(self, host: str, *, user: str, password: str, logmech: str) -> None:

        check_type_compatibility(host, str)
        check_type_compatibility(user, str)
        check_type_compatibility(password, str)
        check_type_compatibility(logmech, str)

        self.host = host
        self.user = user
        self.__password = password
        self.logmech = logmech
        self.connection: Optional[teradatasql.TeradataConnection] = None

    def __enter__(self) -> teradatasql.TeradataConnection:
        self.connection = teradatasql.connect(
            f'{{"host": "{self.host}"}}',
            user=self.user,
            password=self.__password,
            logmech=self.logmech
        )
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.connection.close()  # type: ignore
        self.connection = None
        if exc_type is not None:
            raise


def _teradata_context_creator(stack: ExitStack,
                              credentials: PasswordKeeper,
                              **teradata_context_kwargs: str) -> teradatasql.TeradataConnection:

    if 'user' not in teradata_context_kwargs:
        teradata_context_kwargs['user'] = credentials.get_username()
    if 'password' not in teradata_context_kwargs:
        teradata_context_kwargs['password'] = credentials.get_password()
    conn = stack.enter_context(TeradataContextManager(**teradata_context_kwargs))
    return conn


class TeradataLoader(SqlLoader):
    __slots__ = ()

    def __init__(self,
                 sql_query: str,
                 *,
                 credentials: Optional[PasswordKeeper] = None,
                 teradata_parameters: Optional[Mapping[str, Any]] = None,
                 output_validator: DataFrameSchema = AnyDataFrame,
                 **read_sql_kwargs: Any) -> None:

        if credentials is None:
            credentials = GlobalTeradataConfig.DEFAULT_CREDENTIALS
            if credentials is None:
                raise TypeError(
                    "If parameter 'credentials' is None "
                    "GlobalTeradataConfig.DEFAULT_CREDENTIALS should be set."
                )
        else:
            check_type_compatibility(credentials, PasswordKeeper)

        if teradata_parameters is None:
            teradata_parameters = GlobalTeradataConfig.DEFAULT_LOGIN_PARAMETERS
            if teradata_parameters is None:
                raise TypeError(
                    "If parameter 'teradata_parameters' is None "
                    "GlobalTeradataConfig.DEFAULT_LOGIN_PARAMETERS should be set."
                )
        else:
            check_type_compatibility(teradata_parameters, _Mapping, 'Mapping')

        for teradata_keyword in ('host', 'logmech'):
            if teradata_keyword not in teradata_parameters:
                raise KeyError(f"Parameter 'teradata_parameters' should contain '{teradata_keyword}' key")

        super().__init__(
            _teradata_context_creator,
            sql_query,
            context_creator_args=(credentials,),
            context_creator_kwargs=copy(teradata_parameters),
            read_sql_kwargs=read_sql_kwargs,
            output_validator=output_validator
        )

    @final
    @property
    def credentials(self) -> PasswordKeeper:
        return self._context_creator_args[0]

    @final
    @property
    def teradata_parameters(self) -> Dict[str, Any]:
        res = dict(self._context_creator_kwargs)
        if 'password' in res:
            res['password'] = '*****'
        return res


class _GlobalTeradataConfigType(GlobalConfigType):
    __slots__ = ()


GlobalTeradataConfig = _GlobalTeradataConfigType()
