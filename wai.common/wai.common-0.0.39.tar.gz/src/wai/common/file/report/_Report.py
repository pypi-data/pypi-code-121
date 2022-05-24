from numbers import Real
from typing import Any, Dict, List, Union, Optional

from . import constants
from ._DataType import DataType
from ._Field import Field
from ._AbstractField import AbstractField
from ._PrefixOnlyField import PrefixOnlyField
from ._SuffixOnlyField import SuffixOnlyField
from ._PrefixField import PrefixField
from ._SuffixField import SuffixField


class Report:
    """
    Python implementation of the Report class in the adams-base -> adams-core -> adams.data.report package.
    """
    def __init__(self):
        # Store Header parameters ( parameter:value )
        self._params: Dict[AbstractField, Any] = {}

        # Fields
        self._fields: Dict[str, AbstractField] = {}

        # The database ID of the data structure this report belongs to
        self.database_id: int = constants.NO_ID

        self.init_fields()

    def init_fields(self):
        """
        Set field types.
        """
        self._fields = {}

        self.add_field(Field(constants.FIELD_DUMMYREPORT, DataType.BOOLEAN))
        self.add_field(Field(constants.FIELD_EXCLUDED, DataType.BOOLEAN))

    def add_field(self, field: AbstractField):
        """
        Adds the given field.

        :param field:   The field to add.
        """
        self._fields[field.name] = field

    def has_field(self, field: AbstractField) -> bool:
        """
        Checks whether the field is already stored.

        :param field:   The field to check.
        :return:        True if already added.
        """
        return field.name in self._fields

    def get_field_type(self, field: AbstractField) -> DataType:
        """
        Returns the type for the given field. Either based on the stored
        fields or DataType.UNKNOWN.

        :param field:   The field to look for.
        :return:        The stored field type or DataType.UNKNOWN if field not stored.
        """
        if self.has_field(field):
            return self._fields[field.name].datatype

        return DataType.UNKNOWN

    def get_fields(self, fix: Union[PrefixOnlyField, SuffixOnlyField, None] = None) -> List[AbstractField]:
        """
        Gets all fields as a list.

        :param fix: The common prefix/suffix to match, or none to get all.
        :return:    The fields.
        """
        # Decide the match criteria for the fields
        if isinstance(fix, PrefixOnlyField):
            to_match = fix.get_prefix()

            def field_matcher(field: AbstractField) -> bool:
                return field.is_compound() and field.get_prefix() == to_match
        elif isinstance(fix, SuffixOnlyField):
            to_match = fix.get_suffix()

            def field_matcher(field: AbstractField) -> bool:
                return field.is_compound() and field.get_suffix() == to_match
        else:
            def field_matcher(field: AbstractField) -> bool:
                return True

        return [field for field in self._params.keys() if field_matcher(field)]

    def get_prefix_fields(self) -> List[PrefixOnlyField]:
        """
        Returns all distinct prefix fields.

        :return:    The prefix fields.
        """
        # Get the unique prefix fields as a set
        result = {PrefixField(field) for field in self._params.keys() if field.is_compound()}

        # Put the prefix fields into a sorted list
        result = list(result)
        result.sort()

        return result

    def get_suffix_fields(self) -> List[SuffixOnlyField]:
        """
        Returns all distinct suffix fields.

        :return:    The suffix fields.
        """
        # Get the unique prefix fields as a set
        result = {SuffixField(field) for field in self._params.keys() if field.is_compound()}

        # Put the prefix fields into a sorted list
        result = list(result)
        result.sort()

        return result

    def add_parameter(self, key: str, value: Any):
        """
        Add parameter value to store.

        :param key:     The key.
        :param value:   The value for the key.
        """
        # Get the string representation of this value
        value_string: str = str(value)

        # Get the field for this parameter
        field: Optional[AbstractField] = self._fields[key] if key in self._fields else None

        # Create a new field for the parameter if we don't have one already
        if field is None:
            fixed_string: str = Field.fix_string(value_string)
            datatype: DataType = DataType.UNKNOWN \
                if isinstance(value, str) \
                else DataType.guess_type(fixed_string)
            self._params[Field(key, datatype)] = fixed_string
        else:
            obj = field.value_of(value_string)
            if obj is None:
                return
            self._params[field] = obj if isinstance(value, str) else value

    def set_params(self, params: Dict[AbstractField, Any]):
        """
        Set the parameters.

        :param params:  Dict of parameters.
        """
        self._params = params

    def get_params(self) -> Dict[AbstractField, Any]:
        """
        Get the parameters.

        :return:    Dict of parameters.
        """
        return self._params

    def has_value(self, key: Union[AbstractField, str]) -> bool:
        """
        Returns whether a certain value is available in this report.

        :param key: The value to look for.
        :return:    True if the value is available.
        """
        if isinstance(key, str):
            key = Field(key, DataType.UNKNOWN)

        return self.get_value(key) is not None

    def has_values(self, fields: List[Union[AbstractField, str]]) -> bool:
        """
        Checks whether all the fields are available.

        :param fields:  The required fields.
        :return:        True if required fields are available.
        """
        return all(map(self.has_field, fields))

    def set_value(self, key: AbstractField, value: Any) -> bool:
        """
        Sets a value.

        :param key:     The key of the value.
        :param value:   The new value.
        :return:        Whether successfully set.
        """
        if isinstance(value, str):
            value = Field.fix_string(value)

        # Convert to the correct type
        try:
            value = key.datatype.convert(value)
        except Exception:
            return False

        self._params[key] = value
        if key.name in self._fields:
            self._fields[key.name] = key

        return True

    def set_numeric_value(self, key: str, value: Real):
        """
        Sets a numeric value.

        :param key:     The key of the value.
        :param value:   The new value.
        """
        self.set_value(Field(key, DataType.NUMERIC), value)

    def set_string_value(self, key: str, value: str):
        """
        Sets a string value.

        :param key:     The key of the value.
        :param value:   The new value.
        """
        self.set_value(Field(key, DataType.STRING), value)

    def set_boolean_value(self, key: str, value: bool):
        """
        Sets a boolean value.

        :param key:     The key of the value.
        :param value:   The new value.
        """
        self.set_value(Field(key, DataType.BOOLEAN), value)

    def get_value(self, key: AbstractField) -> Any:
        """
        Gets parameter value, or None if not available.

        :param key:     The key.
        :return:        Parameter value.
        """
        return self._params[key] if key in self._params else None

    def get_string_value(self, key: Union[str, AbstractField]) -> Optional[str]:
        """
        Gets parameter value, or None if not available.

        :param key:     The key.
        :return:        Parameter value.
        """
        if isinstance(key, str):
            key = Field(key, DataType.STRING)

        return str(self._params[key]) if key in self._params else None

    def get_boolean_value(self, key: Union[str, AbstractField]) -> Optional[bool]:
        """
        Gets parameter value, or None if not available.

        :param key:     The key.
        :return:        Parameter value.
        """
        if isinstance(key, str):
            key = Field(key, DataType.BOOLEAN)

        return self._params[key] if key in self._params and isinstance(self._params[key], bool) else None

    def get_real_value(self, key: Union[str, AbstractField]) -> Optional[Real]:
        """
        Gets parameter value, or None if not available.

        :param key:     The key.
        :return:        Parameter value.
        """
        if isinstance(key, str):
            key = Field(key, DataType.NUMERIC)

        return self._params[key] if key in self._params and isinstance(self._params[key], Real) else None

    def remove_value(self, key: AbstractField) -> Any:
        """
        Removes the specified field.

        :param key:     The key.
        :return:        The value previously stored in the report, or None if the field wasn't present.
        """
        return self._params.pop(key, None)

    def update(self):
        """
        Updates certain dependant fields. This method should be called before
        saving it to the database, after loading it from the database or when
        a quantitation report has been created by hand.

        Default implementation does nothing.
        """
        pass

    def to_string(self) -> str:
        """
        Returns the string representation of a report.

        :return:    String representation of report.
        """
        # Sort the fields into a list
        fields = list(self._params.keys())
        fields.sort()

        return "\n".join(
            f"{field.to_parseable_string()}: {self._params[field]}"
            for field in fields
        )

    def get_clone(self) -> "Report":
        """
        Returns a clone of itself.

        :return:    The clone.
        """
        # Create a new instance of this report type
        clone: Report = self.new_instance()

        # Assign our contents to the clone
        if clone is not None:
            clone.assign(self)

        return clone

    def assign(self, other: "Report"):
        """
        Obtains all the values from the specified report.

        :param other:   The report to obtain the values from.
        """
        self._fields = dict(other._fields)
        self._params = dict(other._params)
        self.database_id = other.database_id

    def set_dummy_report(self, value: bool):
        """
        Sets whether this report is dummy report or not.

        :param value:   If true then this report will be flagged as dummy report.
        """
        self.add_parameter(constants.FIELD_DUMMYREPORT, value)

    def is_dummy_report(self) -> bool:
        """
        Returns whether this report is a dummy report or not.

        :return:    True if this report is a dummy report.
        """
        return self.get_boolean_value(constants.FIELD_DUMMYREPORT) is True

    def compare_to(self, obj: Any) -> int:
        """
        Compares this object with the specified object for order.  Returns a
        negative integer, zero, or a positive integer as this object is less
        than, equal to, or greater than the specified object.

        :param obj:     The object to be compared.
        :return:        A negative integer, zero, or a positive integer as this object
                        is less than, equal to, or greater than the specified object.
        """
        raise NotImplementedError(Report.compare_to.__qualname__)

    def __eq__(self, other: Any):
        return isinstance(other, Report) and self._params == other._params

    def intersect(self, report: "Report") -> "Report":
        """
        Returns the intersection with this Quantitation Report and the provided
        one. The result contains the values of this quantitation report. No
        merging of values between the two is performed.

        :param report:  The report to get the intersection with.
        :return:        The intersection.
        """
        # Create a new report
        result: Report = self.new_instance()

        # Add the intersecting parameters
        if result is not None:
            result.set_params({key: self.get_value(key)
                               for key in self.get_fields()
                               if report.has_value(key)})

        return result

    def minus(self, report: "Report") -> "Report":
        """
        Returns the subset of values that this Quantitation Report contains, but
        not the provided one. The result contains the values of this quantitation
        report.

        :param report:  The report to get the fields to exclude from.
        :return:        The new report.
        """
        # Create a new report
        result: Report = self.new_instance()

        # Add the non-intersecting parameters
        if result is not None:
            result.set_params({key: self.get_value(key)
                               for key in self.get_fields()
                               if not report.has_value(key)})

        return result

    def merge_with(self, other: "Report"):
        """
        Merges its own data with the one provided by the specified object.
        Never overwrites its own values, only adds missing ones.

        :param other:   The object to merge with.
        """
        for field in other.get_fields():
            if not self.has_value(field):
                self.set_value(field, other.get_value(field))

    @classmethod
    def new_instance(cls) -> Optional["Report"]:
        """
        Returns a new instance of the concrete subclass for the report.

        :return:    The new instance.
        """
        try:
            return cls()
        except Exception:
            return None

    def to_properties(self) -> Dict[str, Any]:
        """
        Turns the report into a properties object. Also adds the parent ID.

        :return:
        """
        # Create properties with the parent ID
        result: Dict[str, Any] = {constants.PROPERTY_PARENTID: str(self.database_id)}

        # Transfer properties
        for field in self.get_fields():
            value = self.get_value(field)
            result[field.name] = str(value)
            result[field.name + constants.DATATYPE_SUFFIX] = str(DataType.guess_type(value))

        return result

    def __iter__(self):
        return iter(self.get_fields())

    def __contains__(self, item):
        return self.has_field(item)

    def __getitem__(self, item):
        return self.get_value(item)

    def __setitem__(self, key, value):
        self.set_value(key, value)

    def __str__(self):
        return self.to_string()
