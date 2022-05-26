import hashlib
import hmac
from dataclasses import dataclass
from json import JSONDecodeError, dumps, loads
from logging import getLogger
from typing import Any, List, Optional, Tuple, Union

from jsonpath_ng.ext import parse
from jsonpath_ng.jsonpath import DatumInContext, JSONPath
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.util.types import AttributeValue

from helios.base.span_attributes import SpanAttributes

_LOG = getLogger(__name__)
DATA_TO_DROP = [SpanAttributes.DB_QUERY_RESULT, SpanAttributes.HTTP_RESPONSE_BODY]
DATA_TO_OBFUSCATE = [SpanAttributes.DB_STATEMENT, SpanAttributes.HTTP_REQUEST_BODY, SpanAttributes.MESSAGING_PAYLOAD]
ExpectedValueType = Optional[Union[str, float, int, bool]]


@dataclass
class DataObfuscatorConfiguration:
    allowlist: Optional[List[Union[str, Tuple[str, ExpectedValueType]]]]
    hmac_key: str


class DataObfuscator:
    _allowlist: List[JSONPath]
    _extended_allowlist: List[Tuple[JSONPath, ExpectedValueType]]
    _hmac_key: str

    def __init__(self, data_obfuscator_configuration: DataObfuscatorConfiguration):
        allowlist: List[str] = []
        extended_allowlist: List[Tuple[str, ExpectedValueType]] = []

        if data_obfuscator_configuration.allowlist is not None:
            for item in data_obfuscator_configuration.allowlist:
                if isinstance(item, str):
                    allowlist.append(item)
                elif DataObfuscator._is_valid_allowlist_tuple(item):
                    extended_allowlist.append(item)
                else:
                    _LOG.debug(f'Ignoring invalid allowlist item {item}.')

        self._allowlist = DataObfuscator._parse_path_expressions(allowlist)
        self._extended_allowlist = DataObfuscator._parse_extended_allowlist(extended_allowlist)
        self._hmac_key = data_obfuscator_configuration.hmac_key

    def obfuscate_data(self, span: ReadableSpan) -> None:
        # noinspection PyProtectedMember
        attributes = span._attributes

        if attributes is None:
            return

        for datum_to_drop in DATA_TO_DROP:
            if datum_to_drop in attributes:
                # noinspection PyUnresolvedReferences
                del attributes[datum_to_drop]

        for datum_to_obfuscate in DATA_TO_OBFUSCATE:
            if datum_to_obfuscate in attributes:
                value = attributes[datum_to_obfuscate]
                # noinspection PyUnresolvedReferences
                attributes[datum_to_obfuscate] = self._obfuscate_datum(value)

    @staticmethod
    def hash(key: str, msg: Any, length: int = 8) -> str:
        return hmac.new(key.encode(), str(msg).encode(), hashlib.sha256).hexdigest()[:length]

    @staticmethod
    def _is_valid_allowlist_tuple(allowlist_tuple: Tuple[str, ExpectedValueType]) -> bool:
        if isinstance(allowlist_tuple, (list, tuple)) and len(allowlist_tuple) == 2:
            path_expression, expected_value = allowlist_tuple
            is_valid_path_expression = isinstance(path_expression, str)
            is_valid_expected_value = expected_value is None or isinstance(expected_value, (str, float, int, bool))
            return is_valid_path_expression and is_valid_expected_value

        return False

    @staticmethod
    def _parse_path_expressions(allowlist: List[str]) -> List[JSONPath]:
        parsed_path_expressions: List[JSONPath] = []

        for path_expression in allowlist:
            try:
                parsed_path_expressions.append(parse(path_expression))
            except Exception as exception:
                _LOG.debug(f'Ignoring invalid path expression {path_expression}.', exception)

        return parsed_path_expressions

    @staticmethod
    def _parse_extended_allowlist(
            extended_allowlist: List[Tuple[str, ExpectedValueType]]
    ) -> List[Tuple[JSONPath, ExpectedValueType]]:
        parsed_extended_allowlist: List[Tuple[JSONPath, ExpectedValueType]] = []

        for path_expression, expected_value in extended_allowlist:
            try:
                parsed_path_expression = parse(path_expression)
            except Exception as exception:
                _LOG.debug(f'Ignoring invalid path expression {path_expression}.', exception)
                parsed_path_expression = None

            if parsed_path_expression is not None:
                parsed_extended_allowlist.append((parsed_path_expression, expected_value))

        return parsed_extended_allowlist

    def _obfuscate_datum(self, value: AttributeValue) -> AttributeValue:
        if isinstance(value, str):
            dict_or_list: Optional[Union[dict, list]]

            try:
                dict_or_list = loads(value)
            except JSONDecodeError:
                dict_or_list = None

            if dict_or_list is not None:
                if self._skip_object_obfuscation(dict_or_list):
                    return value

                nodes = self._extract_nodes(dict_or_list)
                obfuscated_dict_or_list = self._obfuscate_object(dict_or_list)
                self._insert_nodes(obfuscated_dict_or_list, nodes)
                return dumps(obfuscated_dict_or_list)

        return self._obfuscate_primitive(value)

    def _skip_object_obfuscation(self, dict_or_list: Union[dict, list]) -> bool:
        for parsed_path_expression, expected_value in self._extended_allowlist:
            try:
                nodes = parsed_path_expression.find(dict_or_list)
            except Exception as exception:
                _LOG.debug(f'Cannot extract nodes of parsed path expression {parsed_path_expression}.', exception)
                nodes = []

            for node in nodes:
                if node.value == expected_value:
                    return True

        return False

    def _extract_nodes(self, dict_or_list: Union[dict, list]) -> List[DatumInContext]:
        nodes: List[DatumInContext] = []

        for parsed_path_expression in self._allowlist:
            try:
                nodes.extend(parsed_path_expression.find(dict_or_list))
            except Exception as exception:
                _LOG.debug(f'Cannot extract nodes of parsed path expression {parsed_path_expression}.', exception)

        return nodes

    @staticmethod
    def _insert_nodes(dict_or_list: Union[dict, list], nodes: List[DatumInContext]) -> None:
        for node in nodes:
            try:
                parse(str(node.full_path)).update(dict_or_list, node.value)
            except Exception as exception:
                _LOG.debug(f'Cannot insert node {node} into dictionary or list.', exception)

    def _obfuscate_object(self, object_to_obfuscate: Any) -> Any:
        if isinstance(object_to_obfuscate, dict):
            return {key: self._obfuscate_object(value) for key, value in object_to_obfuscate.items()}
        elif isinstance(object_to_obfuscate, list):
            return [self._obfuscate_object(value) for value in object_to_obfuscate]
        else:
            return self._obfuscate_primitive(object_to_obfuscate)

    def _obfuscate_primitive(self, primitive: Any) -> Any:
        if primitive is None or isinstance(primitive, bool):
            return primitive

        try:
            return DataObfuscator.hash(self._hmac_key, primitive)
        except Exception as exception:
            _LOG.debug(f'Cannot hash primitive {primitive}.', exception)
            return '********'
