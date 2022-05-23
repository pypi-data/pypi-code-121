import pandas as pd

from lumipy.common.string_utils import indent_str
from .direct_provider_base import DirectProviderBase
from ..sql_value_type import SqlValType
from functools import reduce


def build_def_sql(*args):
    if len(args) == 0:
        return ''

    if len(args) > 1:
        qry = reduce(lambda x, y: x.union(y), map(lambda a: a.select('*'), args))
    else:
        qry = args[0].select('*')

    chunks = qry.get_sql().split(';')[:-1]
    return ';'.join(chunks) + ';'


class PeekableDirectProvider(DirectProviderBase):

    def __init__(self, client, provider_name, body, limit, with_vars, **kwargs):

        def sql_def_str(peek):

            lim_str = f' limit {limit}' if limit is not None else ''
            lim = ' limit 1' if peek else lim_str
            args_str = '\n'.join([f'--{k}={v}' for k, v in kwargs.items()])

            if len(body) > 0:
                body_strs = '----\n'.join(body)
                args_str += f'\n----\n{body_strs}'

            if len(with_vars) > 0:
                with_str = ' with ' + ', '.join(v.get_sql() for v in with_vars)
            else:
                with_str = ''

            return f"""use {provider_name}{with_str}{lim}
                {indent_str(args_str, 4)}
            enduse"""

        at_var_def = build_def_sql(*with_vars)
        peek_sql = f'--peek sql for {provider_name}\n'
        peek_sql += f'{at_var_def}\n\n@x = {sql_def_str(True)};\n'
        peek_sql += f'select * from @x'

        top_row = client.query_and_fetch(peek_sql)

        if top_row.shape[0] == 0:
            raise ValueError(
                f"Could not build column content for {provider_name} by peeking at the top row 👀.\n"
                f"Peek query used the following SQL:\n\n{indent_str(peek_sql, 4)}\n\nbut nothing was returned."
            )

        names = top_row.columns
        types = [self.__infer_type_of_str(s) for s in top_row.iloc[0].tolist()]
        # Type inference
        type_guide = {c: t for c, t in zip(names, types)}

        hash_val = hash(''.join(map(lambda x: str(x), kwargs.values())))
        var_name = f"{provider_name.replace('.', '_').lower()}_{str(hash_val)[1:5]}"
        super().__init__(
            sql_def_str(False),
            var_name,
            type_guide,
            client,
            *with_vars
        )

    # noinspection PyBroadException
    @staticmethod
    def __infer_type_of_str(s: str) -> SqlValType:

        if isinstance(s, int):
            return SqlValType.Int
        elif isinstance(s, float):
            return SqlValType.Double

        try:
            pd.to_datetime(s)
            return SqlValType.DateTime
        except Exception:
            return SqlValType.Text

