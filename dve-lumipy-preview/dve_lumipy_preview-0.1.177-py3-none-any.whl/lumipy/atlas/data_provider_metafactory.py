from typing import Callable

from lumipy.atlas.base.base_provider_metafactory import BaseProviderMetafactory
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.table.base_source_table import SourceTable
from lumipy.query.expression.table.table_parameter_assignment import ParameterAssignment


class _DataProviderMetafactory(BaseProviderMetafactory):

    @classmethod
    def _create_call_fn(
            mcs, table_name, description, provider_type, category, last_ping_at, documentation, fields, client
    ) -> Callable:

        pmeta = [f for f in fields if f.field_type == 'Parameter']
        cmeta = [f for f in fields if f.field_type == 'Column']

        ps = {p.name: p for p in pmeta}

        # Create the replacement __call__ method
        def __call__(self, **kwargs):

            assignments = {}
            for k, v in kwargs.items():
                if k not in ps.keys():
                    msg = f"'{k}' is not a valid parameter of {self._name}.\n"
                    if len(ps) > 0:
                        ljust = max([len(n) for n in ps.keys()])
                        plist = '\n  •'.join(map(lambda x: f"{x.name.ljust(ljust)}  ({x.data_type.name})", ps.values()))
                        msg += f"Valid parameters are:\n  •{plist}."
                    else:
                        msg += f"This provider does not have any parameters: try doing 'provider()'."
                    raise ValueError(msg)

                assignments[k] = ParameterAssignment(ps[k], v)

            parents = list(assignments.values()) + [self]
            table_hash = hash(sum(hash(p) for p in parents))
            columns = [SourceColumn(c, table_hash, with_brackets=True) for c in cmeta]

            return SourceTable(
                f'[{self.get_table_name()}]',
                columns,
                self.get_client(),
                'define source table',
                assignments,
                *parents
            )

        signature = mcs._generate_call_signature(pmeta, SourceTable)
        __call__.__signature__ = signature
        __call__.__doc__ = mcs._generate_call_docstring(pmeta, signature, table_name, description, documentation)

        return __call__
