from typing import Callable

import datetime as dt
from lumipy.atlas.base.base_provider_metafactory import BaseProviderMetafactory
from lumipy.query.expression.direct_provider.peekable_direct_provider import PeekableDirectProvider
from lumipy.query.expression.direct_provider.fixed_shape_direct_provider import FixedShapeDirectProvider
from lumipy.query.expression.variable.base_variable import BaseVariable


class _DirectProviderMetafactory(BaseProviderMetafactory):

    @classmethod
    def _create_call_fn(
            mcs, table_name, description, provider_type, category, last_ping_at, documentation, fields, client
    ) -> Callable:

        pmeta = [f for f in fields if f.field_type == 'Parameter']
        cmeta = [f for f in fields if f.field_type == 'Column']

        ps = {p.name: p for p in pmeta}

        body = sorted(
            [f for f in pmeta if f.body_param_order is not None],
            key=lambda x: x.body_param_order
        )
        body = [f.get_name() for f in body]

        name_map = {p.name: p.field_name for p in pmeta}

        def val_map(v):
            if isinstance(v, (dt.datetime, dt.date)):
                return v.strftime('%Y-%m-%dT%H:%M:%S')

            return v

        # Create the replacement __call__ method
        def __call__(self, *with_vars, **kwargs):
            for k, v in kwargs.items():
                if k not in ps.keys() and k != 'apply_limit':
                    msg = f"'{k}' is not a valid parameter of {table_name}.\n"
                    if len(ps) > 0:
                        ljust = max([len(n) for n in ps.keys()])
                        plist = '\n  •'.join(map(lambda x: f"{x.name.ljust(ljust)}  ({x.data_type.name})", ps.values()))
                        msg += f"Valid parameters are:\n  •{plist}."
                    else:
                        msg += f"This provider does not have any parameters: try doing 'provider()'."
                    raise ValueError(msg)

            for a in with_vars:
                if not isinstance(a, BaseVariable):
                    raise TypeError(
                        f"Positional args to direct providers must be luminesce table or scalar variables. "
                        f"Received a value of type: {type(a).__name__}.\n"
                        "You may need to call .to_table_var() / .to_scalar_var() or check for a missing keyword."
                    )

            mapped_kw = {name_map[k]: val_map(v) for k, v in kwargs.items() if k not in body and k != 'apply_limit'}
            body_strs = [kwargs[b] for b in body if b in kwargs.keys()]
            limit = kwargs['apply_limit'] if 'apply_limit' in kwargs.keys() else None

            # if fixed output shape, switch here
            if len(cmeta) > 0:
                return FixedShapeDirectProvider(client, table_name, cmeta, body_strs, limit, with_vars, **mapped_kw)
            else:
                return PeekableDirectProvider(client, table_name, body_strs, limit, with_vars, **mapped_kw)

        if len(cmeta) > 0:
            signature = mcs._generate_call_signature(pmeta, FixedShapeDirectProvider, True, True)
        else:
            signature = mcs._generate_call_signature(pmeta, PeekableDirectProvider, True, True)

        __call__.__signature__ = signature
        __call__.__doc__ = mcs._generate_call_docstring(pmeta, signature, table_name, description, documentation)

        return __call__
