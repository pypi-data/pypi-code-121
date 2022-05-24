import re

from . import CoreService_pb2 as pb
from . import FeatureSetProtoApi_pb2 as FeatureSetApi


class FeatureSchemaSpecialData:
    def __init__(
        self, spi=False, pci=False, rpi=False, demographic=False, sensitive=False
    ):
        self.spi = spi
        self.pci = pci
        self.rpi = rpi
        self.demographic = demographic
        self.sensitive = sensitive

    def __repr__(self):
        return f"spi={self.spi}, pci={self.pci}, rpi={self.rpi}, demographic={self.demographic}, sensitive={self.sensitive}"


class FeatureSchema:
    def __init__(
        self,
        name,
        _data_type,
        special_data=None,
        nested_features_schema=None,
        _feature_type="AUTOMATIC_DISCOVERY",
        description="",
        classifier="",
    ):
        self._data_type = _data_type
        self._name = name
        self._special_data = special_data or FeatureSchemaSpecialData()
        self._nested_features_schema = nested_features_schema or []
        self._schema = Schema(self._nested_features_schema, False)
        self._validated_feature_type = FeatureSchema.get_and_validate_feature_type(
            _feature_type
        )
        self._description = description
        self._classifier = classifier

    @property
    def schema(self):
        return self._schema

    @property
    def special_data(self):
        return self._special_data

    @property
    def name(self):
        return self._name

    @property
    def data_type(self):
        if self._schema.size() > 0:
            return self._data_type.format(self._schema.to_string())
        else:
            return self._data_type

    @data_type.setter
    def data_type(self, value):
        self._data_type = value

    @property
    def feature_type(self):
        return FeatureSetApi.FeatureType.Name(self._validated_feature_type)

    @feature_type.setter
    def feature_type(self, value):
        self._validated_feature_type = FeatureSchema.get_and_validate_feature_type(
            value
        )

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def classifier(self):
        return self._classifier

    @classifier.setter
    def classifier(self, value):
        self._classifier = value

    @property
    def schema(self):
        return self._schema

    def to_string(self):
        return self.data_type

    @staticmethod
    def create_from(feature):
        nested = [
            FeatureSchema.create_from(nested_feature)
            for _, nested_feature in feature.nested_features.items()
        ]
        return FeatureSchema(
            feature.name,
            feature.data_type,
            FeatureSchemaSpecialData(
                feature.special_data.spi,
                feature.special_data.pci,
                feature.special_data.rpi,
                feature.special_data.demographic,
                feature.special_data.sensitive,
            ),
            nested,
            feature.profile.feature_type,
            feature.description,
            feature.classifier,
        )

    @staticmethod
    def get_and_validate_feature_type(feature_type):
        valid_values = FeatureSetApi.FeatureType.keys()
        if feature_type.upper() in valid_values:
            FeatureSetApi.FeatureType.Value(feature_type.upper())
        else:
            raise Exception(
                "Invalid feature type. Supported values are: "
                + ", ".join(map(str, valid_values))
            )

    def __repr__(self):
        return self.to_string()


class Schema:
    def __init__(self, feature_schemas, is_root_schema):
        self._feature_schemas = feature_schemas
        self._is_root_schema = is_root_schema
        if is_root_schema:
            self._field_separator = " "
        else:
            self._field_separator = " : "

    def __getitem__(self, feature_name):
        filtered = list(filter(lambda f: f.name == feature_name, self._feature_schemas))
        if len(filtered):
            return filtered[0]
        else:
            raise Exception(
                f"Feature name '{feature_name}' does not exist in the schema."
            )

    @staticmethod
    def create_from(obj):
        from .entities.feature_set import FeatureSet

        if isinstance(obj, FeatureSet):
            features = [
                FeatureSchema.create_from(feature)
                for name, feature in obj.features.items()
            ]
            return Schema(features, True)
        elif isinstance(obj, str):
            return Schema(Schema._parse_features_schema(obj, True)[::-1], True)
        else:
            raise Exception(
                "Schema can be created either from string or existing feature set."
            )

    def select(self, feature_names):
        self._feature_schemas = list(
            filter(lambda schema: schema.name in feature_names, self._feature_schemas)
        )
        return self

    def exclude(self, feature_names):
        self._feature_schemas = list(
            filter(
                lambda schema: schema.name not in feature_names, self._feature_schemas
            )
        )
        return self

    def append(self, feature_schema, after=None):
        if not after:
            self._feature_schemas.append(feature_schema)
        else:
            index = self._feature_schemas.index(after) + 1
            self._feature_schemas.insert(index, feature_schema)
        return self

    def prepend(self, feature_schema, before=None):
        if not before:
            self._feature_schemas.insert(0, feature_schema)
        else:
            index = self._feature_schemas.index(before)
            self._feature_schemas.insert(index, feature_schema)
        return self

    def size(self):
        return len(self._feature_schemas)

    def to_string(self):
        return ", ".join(
            [
                f"{feature_schema.name}{self._field_separator}{feature_schema.data_type}"
                for feature_schema in self._feature_schemas
            ]
        )

    def _to_proto_schema(self):
        return [
            pb.FeatureSchema(
                name=feature_schema.name,
                data_type=feature_schema.data_type,
                nested=feature_schema.schema._to_proto_schema(),
                special_data=pb.FeatureSchema.SpecialData(
                    spi=feature_schema.special_data.spi,
                    pci=feature_schema.special_data.pci,
                    rpi=feature_schema.special_data.rpi,
                    demographic=feature_schema.special_data.demographic,
                    sensitive=feature_schema.special_data.sensitive,
                ),
                feature_type=feature_schema._validated_feature_type,
                description=feature_schema.description,
                classifier=feature_schema.classifier,
            )
            for feature_schema in self._feature_schemas
        ]

    def __repr__(self):
        return self.to_string()

    @staticmethod
    def _parse_features_schema(schema_string, is_root_level):
        if schema_string:
            feature_schema, remaining_schema_string = Schema._extract_pair(
                schema_string, is_root_level
            )
            return Schema._parse_features_schema(
                remaining_schema_string, is_root_level
            ) + [feature_schema]
        else:
            return []

    @staticmethod
    def _get_index_of_matching_ending_angular_bracket(string):
        stack = []
        for idx, ch in enumerate(string):
            if ch == "<":
                stack.append(idx)
            elif ch == ">":
                if len(stack) == 1:
                    return idx
                else:
                    stack.pop()

    @staticmethod
    def _extract_pair(schema, is_root_level):
        if is_root_level:
            splits = schema.split()
            remaining_with_data_type = " ".join(splits[1:])
        else:
            splits = re.split(r"\s*:\s*", schema)
            remaining_with_data_type = " : ".join(splits[1:])
        col_name = splits[0]
        placeholder = None
        if Schema._is_complex(remaining_with_data_type):
            idx = (
                Schema._get_index_of_matching_ending_angular_bracket(
                    remaining_with_data_type
                )
                + 1
            )
            nested_data_type, remaining_schema = (
                remaining_with_data_type[: idx + 1],
                remaining_with_data_type[idx + 1 :],
            )
            if remaining_with_data_type.upper().startswith("STRUCT"):
                nested_features_schema, placeholder = Schema._extract_struct(
                    nested_data_type
                )
            else:
                nested_features_schema, placeholder = Schema._extract_array(
                    nested_data_type
                )
            if remaining_schema:
                data_type = placeholder or nested_data_type
                rest = " ".join(
                    [split.strip() for split in remaining_schema.split(",")][1:]
                )
                nested_schema = nested_features_schema
            else:
                data_type = placeholder or nested_data_type
                rest = ""
                nested_schema = nested_features_schema
        else:
            data_type, rest, nested_schema = Schema._extract_primitive(
                remaining_with_data_type
            )
        return (
            FeatureSchema(col_name, data_type, nested_features_schema=nested_schema),
            rest,
        )

    @staticmethod
    def _is_complex(data_type):
        first_non_array_type = Schema._extract_first_non_array_data_type(data_type)
        return first_non_array_type.upper().startswith("STRUCT")

    @staticmethod
    def _extract_first_non_array_data_type(data_type):
        if data_type.upper().startswith("ARRAY"):
            nested_data_type = re.split(
                r"\s+<", data_type[len("ARRAY") + 1 : len(data_type) - 1]
            )[-1].strip()
            return Schema._extract_first_non_array_data_type(nested_data_type)
        else:
            return data_type

    @staticmethod
    def _extract_struct(data_type):
        nested_data_type = re.split(
            r"\s+<", data_type[len("STRUCT") + 1 : len(data_type) - 1]
        )[-1].strip()
        return (
            Schema._parse_features_schema(nested_data_type, is_root_level=False)[::-1],
            "STRUCT<{0}>",
        )

    @staticmethod
    def _extract_array(data_type):
        nested_data_type = re.split(
            r"\s+<", data_type[len("ARRAY") + 1 : len(data_type) - 1]
        )[-1].strip()
        if nested_data_type.upper().startswith("ARRAY"):
            return Schema._extract_array(nested_data_type)
        elif nested_data_type.upper().startswith("STRUCT"):
            inner, placeholder = Schema._extract_struct(nested_data_type)
            return inner, f"ARRAY<{placeholder}>"
        else:
            return [], ""

    @staticmethod
    def _extract_primitive(schema):
        splits = [split.strip() for split in schema.split(",")]
        if len(splits) > 1:
            return splits[0], ", ".join(splits[1:]), []
        else:
            return splits[0], "", []
