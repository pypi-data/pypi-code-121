from lumipy.query.expression.direct_provider.direct_provider_base import DirectProviderBase
from lumipy.common.string_utils import indent_str


class FixedShapeDirectProvider(DirectProviderBase):

    def __init__(self, client, provider_name, columns, body, limit, with_vars, **kwargs):

        args_str = '\n'.join([f'--{k}={v}' for k, v in kwargs.items()])
        if len(body) > 0:
            body_strs = '----\n'.join(body)
            args_str += f'\n----\n{body_strs}'

        if len(with_vars) > 0:
            with_str = 'with ' + ', '.join(v.get_sql() for v in with_vars)
        else:
            with_str = ''

        lim_str = f' limit {limit}' if limit is not None else ''
        sql = f'''use {provider_name} {with_str} {lim_str}
            {indent_str(args_str, 8)}
        enduse'''

        type_guide = {c.field_name: c.get_type() for c in columns}

        hash_val = hash(''.join(map(lambda x: str(x), kwargs.values())))
        var_name = f"{provider_name.replace('.', '_').lower()}_{str(hash_val)[1:5]}"

        super().__init__(sql, var_name, type_guide, client, *with_vars)
