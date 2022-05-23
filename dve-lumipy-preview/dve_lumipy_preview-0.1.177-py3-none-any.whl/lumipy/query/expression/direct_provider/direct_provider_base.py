from lumipy.query.expression.sql_value_type import SqlValType
from lumipy.query.expression.table.base_source_table import SourceTable
from lumipy.query.expression.variable.base_variable import BaseVariable
from typing import Dict
from lumipy.atlas.field_metadata import FieldMetadata
from lumipy.query.expression.column.source_column import SourceColumn


class DirectProviderBase(BaseVariable, SourceTable):
    """

    """

    def __init__(self, provider_sql: str, var_name: str, columns_guide: Dict[str, SqlValType], client, *parents):

        BaseVariable.__init__(
            self,
            '@',
            var_name,
            provider_sql
        )

        if type(columns_guide) != dict:
            print(columns_guide)
            raise TypeError()

        table_name = f"@{var_name}"
        col_defs = [FieldMetadata(
            field_name=name,
            field_type='Column',
            table_name=table_name,
            data_type=val_type,
            is_main=False,
            description='[Not available]',
            is_primary_key=False,
            param_default_value=None,
            table_param_columns=None
        ) for name, val_type in columns_guide.items()]

        source_cols = [SourceColumn(fd, hash(self.get_assignment_sql()), True) for fd in col_defs]
        SourceTable.__init__(
            self,
            table_name,
            source_cols,
            client,
            'direct provider',
            {},
            *col_defs,  # Swap for direct provider definition
            *parents
        )
