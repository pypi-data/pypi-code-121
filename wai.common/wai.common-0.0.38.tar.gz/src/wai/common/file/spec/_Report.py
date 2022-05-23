from typing import Dict, Union

from ._Field import Field, DATATYPE_BOOLEAN, DATATYPE_STRING

# The pre-defined fields of any report
FIELD_DUMMYREPORT           = 'Dummy report'
FIELD_EXCLUDED              = 'Excluded'
FIELD_SAMPLE_ID             = 'Sample ID'
FIELD_SAMPLE_TYPE           = 'Sample Type'
FIELD_FORMAT                = 'Format'
FIELD_INSERT_TIMESTAMP      = 'Insert Timestamp'
FIELD_INSTRUMENT            = 'Instrument'
FIELD_SOURCE                = 'Source'
FIELD_PARENT_ID             = 'Parent ID'

# The ID# for uninitialised ids
NO_ID = -1


class Report:
    """
    Class representing the header meta-data of a spectrum file.
    """
    def __init__(self):
        self.params: Dict[Field, any] = {}
        self.fields: Dict[str, Field] = {}
        self.database_id: int = NO_ID

        self.init_fields()

    def init_fields(self):
        """
        Adds the default fields to the report.
        """
        self.fields = {}
        self.add_field(Field(FIELD_DUMMYREPORT, DATATYPE_BOOLEAN))
        self.add_field(Field(FIELD_EXCLUDED, DATATYPE_BOOLEAN))
        self.add_field(Field(FIELD_SAMPLE_ID, DATATYPE_STRING))
        self.add_field(Field(FIELD_SAMPLE_TYPE, DATATYPE_STRING))
        self.add_field(Field(FIELD_INSERT_TIMESTAMP, DATATYPE_STRING))
        self.add_field(Field(FIELD_INSTRUMENT, DATATYPE_STRING))
        self.add_field(Field(FIELD_FORMAT, DATATYPE_STRING))
        self.add_field(Field(FIELD_SOURCE, DATATYPE_STRING))

    def add_field(self, field: Field):
        """
        Adds a new field to the report.

        :param field:   The field to add.
        """
        self.fields[field.name] = field

    def add_parameter(self, field: Union[str, Field], value: any):
        """
        Sets the parameter value for the given field.

        :param field:   The field to set the value against.
        :param value:   The value to apply to the field.
        """
        # Normalise field to its name
        if isinstance(field, Field):
            field_name = field.name
        else:
            field_name = field

        # Can't set the value of a field we don't have
        if field_name not in self.fields:
            raise ValueError('No field called ' + field_name)

        # Get our field reference for the selected field
        field = self.fields[field_name]

        # Convert the value to the field's type
        value = field.value_of(str(value))

        # Set the value against the field
        self.params[field] = value

        # Remember the parent ID as the database ID
        if field_name == FIELD_PARENT_ID:
            self.database_id = value

    def get_parameter(self, field: Union[str, Field]):
        """
        Gets the value set against the given field.

        :param field:   The field to get the value for.
        :return:        The value stored against the field.
        """
        # Normalise a field name to a field reference
        if isinstance(field, str):
            if field in self.fields:
                field = self.fields[field]
            else:
                return None

        # Return the value stored against the field,
        # or None if there isn't one
        if field in self.params:
            return self.params[field]
        else:
            return None

    def set_id(self, id: str):
        """
        Convenience method to set the value of the Sample ID field.

        :param id:  The value to set the Sample ID field to.
        """
        self.add_parameter(FIELD_SAMPLE_ID, id)

    def get_id(self):
        """
        Convenience method to get the value of the Sample ID field.

        :return:    The value of the Sample ID field.
        """
        return self.get_parameter(FIELD_SAMPLE_ID)
