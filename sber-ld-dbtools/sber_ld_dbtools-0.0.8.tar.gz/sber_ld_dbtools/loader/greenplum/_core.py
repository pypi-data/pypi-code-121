from collections.abc import Mapping as _Mapping
from contextlib import ExitStack
from copy import copy
from typing import Optional, Any, Mapping, Dict

import psycopg2
from pandakeeper.dataloader.sql import SqlLoader
from pandakeeper.validators import AnyDataFrame
from pandera import DataFrameSchema
from typing_extensions import final
from varutils.typing import check_type_compatibility

from sber_ld_dbtools.credentials import PasswordKeeper, set_default_kerberos_principal
from sber_ld_dbtools.loader.config import GlobalConfigType

__all__ = (
    'GreenplumLoader',
    'GlobalGreenplumConfig'
)


def _greenplum_context_creator(stack: ExitStack,
                               credentials: PasswordKeeper,
                               **greenplum_context_kwargs: Any) -> psycopg2.extensions.connection:
    set_default_kerberos_principal(credentials)
    if 'user' not in greenplum_context_kwargs:
        greenplum_context_kwargs['user'] = credentials.get_username()
    conn = stack.enter_context(psycopg2.connect(**greenplum_context_kwargs))
    return conn


class GreenplumLoader(SqlLoader):
    __slots__ = ()

    def __init__(self,
                 sql_query: str,
                 *,
                 credentials: Optional[PasswordKeeper] = None,
                 greenplum_parameters: Optional[Mapping[str, Any]] = None,
                 output_validator: DataFrameSchema = AnyDataFrame,
                 **read_sql_kwargs: Any) -> None:

        if credentials is None:
            credentials = GlobalGreenplumConfig.DEFAULT_CREDENTIALS
            if credentials is None:
                raise TypeError(
                    "If parameter 'credentials' is None "
                    "GlobalGreenplumConfig.DEFAULT_CREDENTIALS should be set."
                )
        else:
            check_type_compatibility(credentials, PasswordKeeper)

        if greenplum_parameters is None:
            greenplum_parameters = GlobalGreenplumConfig.DEFAULT_LOGIN_PARAMETERS
            if greenplum_parameters is None:
                raise TypeError(
                    "If parameter 'greenplum_parameters' is None "
                    "GlobalGreenplumConfig.DEFAULT_LOGIN_PARAMETERS should be set."
                )
        else:
            check_type_compatibility(greenplum_parameters, _Mapping, 'Mapping')

        for keyword in ('host', 'dbname'):
            if keyword not in greenplum_parameters:
                raise KeyError(f"Parameter 'greenplum_parameters' should contain '{keyword}' key")

        super().__init__(
            _greenplum_context_creator,
            sql_query,
            context_creator_args=(credentials,),
            context_creator_kwargs=copy(greenplum_parameters),
            read_sql_kwargs=read_sql_kwargs,
            output_validator=output_validator
        )

    @final
    @property
    def credentials(self) -> PasswordKeeper:
        return self._context_creator_args[0]

    @final
    @property
    def greenplum_parameters(self) -> Dict[str, Any]:
        res = dict(self._context_creator_kwargs)
        if 'password' in res:
            res['password'] = '*****'
        return res


class _GlobalGreenplumConfigType(GlobalConfigType):
    __slots__ = ()


GlobalGreenplumConfig = _GlobalGreenplumConfigType()
