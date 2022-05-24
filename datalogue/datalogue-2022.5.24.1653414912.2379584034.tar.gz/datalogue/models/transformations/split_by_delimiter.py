from datalogue.models.transformations.commons import Transformation
from datalogue.dtl_utils import _parse_string_list, _parse_list
from datalogue.errors import DtlError, _property_not_found
from typing import List, Union


class PathWithIndex(object):
    """
    Represents the associated tuple of a path with an index
    Used when we want to specify fields with a specific order.
    For example, the SplitByDelimiter transformation uses this class to specify the order of output fields
    according to their indices. If a record in the source has a value of 'a','b','c',
    then index 0 would refer to 'a', index 1 to 'b', etc.
    """

    type_str = "PathWithIndex"

    def __init__(self, index: int, path: List[str]):
        self.index = index
        self.path = path

    def __repr__(self):
        return f"PathWithIndex(index= {self.index}, path= {','.join(self.path)})"

    def __eq__(self, other: "PathWithIndex"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def _as_payload(self) -> dict:
        return {"index": self.index, "field": self.path}

    @classmethod
    def _from_payload(cls, json: dict) -> Union[DtlError, "PathWithIndex"]:
        index = json.get("index")
        path = json.get("field")
        if path is None:
            return _property_not_found("field", json)
        if index is None:
            return _property_not_found("index", json)
        return cls(index=index, path=path)


class SplitByDelimiter(Transformation):
    """
    Splits data from one field (source) into multiple fields (target) by delimiter
    """

    type_str = "SplitByDelimiter"

    def __init__(self, path: List[str], delimiter: str, output_paths: List[PathWithIndex]):
        """
        :param path: path in the source data which contains data that user wants to split
        :param delimiter: delimiter used in the source, based on which the user would like to split the data into
        separate fields
        :param output_paths: ordered path for output with indices. After the split is performed on `path`,
        the output array will be assigned to the fields according to their indices.
        """
        Transformation.__init__(self, SplitByDelimiter.type_str)
        self.path = path
        self.delimiter = delimiter
        self.output_paths = output_paths

    def __eq__(self, other: "SplitByDelimiter"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"SplitByDelimiter(path= {self.path}, delimiter= {self.delimiter}, output_paths= {self.output_paths})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["sourceField"] = self.path
        base["delimiter"] = self.delimiter
        base["targetFields"] = list(map(lambda x: x._as_payload(), self.output_paths))
        return base

    @classmethod
    def _from_payload(cls, json: dict) -> Union[DtlError, "SplitByDelimiter"]:
        path = json.get("sourceField")
        delimiter = json.get("delimiter")
        indexed_paths = json.get("targetFields")

        if path is None:
            return _property_not_found("sourceField", json)
        if indexed_paths is None:
            return _property_not_found("targetFields", json)
        if delimiter is None:
            return _property_not_found("delimiter", json)

        output_paths = _parse_list(PathWithIndex._from_payload)(indexed_paths)
        return cls(path=path, delimiter=delimiter, output_paths=output_paths)
