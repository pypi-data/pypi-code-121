from lumipy.common.lockable import Lockable
from lumipy.common.string_utils import sql_str_to_name, connector, prettify_tree, indent_str
from lumipy.query.expression import sql_value_type as lo


class FieldMetadata(Lockable):
    """Represents information defining a single Luminesce provider field (column or parameter).

    Attributes:
        field_name (str): Luminesce field name.
        name (str): pythonic version of the Luminesce field name.
        field_type (str): field type (whether it's a column or parameter)
        table_name (str): Luminesce provider name of field's provider.
        data_type (ArgType): SQL Data type of the field (e.g. Text, Double, Int)
        description (str): Description of the field.
        is_main (bool): Whether the field is selected by 'select ^ from table'.
        is_primary_key (bool): Whether the field is a primary key that uniquely labels a row.
        param_default_value (str): default value if field is a parameter and default exists.
        table_param_columns (str): parameters of the provider.
    """

    @staticmethod
    def from_row(field_row) -> 'FieldMetadata':
        """Build a field definition from a pandas dataframe row pulled from the table and field catalogue.

        Args:
            field_row: pandas dataframe row for the field.

        Returns:
            FieldDefinition: field definition object derived from the row.

        """
        kwargs = {
            "table_name": field_row.TableName,
            "field_name": field_row.FieldName,
            "data_type": lo.SqlValType[field_row.DataType],
            "field_type": field_row.FieldType,
            "is_primary_key": field_row.IsPrimaryKey,
            "is_main": field_row.IsMain,
            "description": field_row.Description_fld,
            "param_default_value": field_row.ParamDefaultValue,
            "table_param_columns": field_row.TableParamColumns
        }
        return FieldMetadata(**kwargs)

    def __init__(self, field_name, field_type,
                 table_name, data_type, is_main, description,
                 is_primary_key, param_default_value, table_param_columns, name_override=None, body_param_order=None):
        """__init__ method of the FieldDefinition class.

        Args:
            field_name (str): Luminesce field name.
            field_type (str): field type (whether it's a column or parameter)
            table_name (str): Luminesce provider name of field's provider.
            data_type (ArgType): SQL Data type of the field (e.g. Text, Double, Int)
            description (str): Description of the field.
            is_main (bool): Whether the field is selected by 'select ^ from table'.
            is_primary_key (bool): Whether the field is a primary key that uniquely labels a row.
            param_default_value (Union[str, None]): default value if field is a parameter and default exists.
            table_param_columns (Union[str, None]): parameters of the provider.
            name_override (str): value to override field's pythonic name with. Otherwise derived from field_name arg.
        """
        def invalid_name(name_str):
            any_bad_char = any(not c.isalnum() and c != '_' for c in name_str)
            first_numeric = name_str[0].isnumeric()
            internal_naming = name_str[0] == '_'
            return any_bad_char or first_numeric or internal_naming

        if name_override is not None and invalid_name(name_override):
            raise ValueError(
                f"Name override in field description was not a valid name for a python member: {name_override}."
            )

        self.field_name = field_name
        self.name = name_override if name_override is not None else sql_str_to_name(self.field_name)
        self.field_type = field_type
        self.table_name = table_name
        self.data_type = data_type
        self.description = description
        self.is_main = is_main
        self.is_primary_key = is_primary_key
        self.param_default_value = param_default_value
        self.table_param_columns = table_param_columns
        self.body_param_order = body_param_order

        super().__init__()

    def __str__(self):
        out = f'{connector}Field Definition: {self.name} ({self.field_name})\n'
        avoid = ['name', '_locked']
        meta_str = "\n".join(
            [f"{connector}{k}: {v}" for k, v in self.__dict__.items() if k not in avoid]
        )
        return prettify_tree(out + indent_str(meta_str))

    def __repr__(self):
        return str(self)

    def get_type(self) -> lo.SqlValType:
        """Get the ArgType enum value representing the datatype of the field.

        Returns:
            ArgType: datatype of the field (e.g. Text, Double)
        """
        return self.data_type

    def get_name(self) -> str:
        """Get the pythonic name of this field.

        Returns:
            str: pythonic field name.
        """
        return self.name
