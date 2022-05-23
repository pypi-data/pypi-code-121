from marshmallow import Schema, class_registry
from abc import ABC, abstractmethod


class TiyaroBase(ABC):
    def __init__(self) -> None:
        self.input_schema = None
        self.output_schema = None

    def def_input_schema(self, schemaDict):
        self.input_schema = Schema.from_dict(schemaDict, name="InputSchema")
        class_registry.register("InputSchema", self.input_schema)

    def def_output_schema(self, schemaDict):
        self.output_schema = Schema.from_dict(schemaDict, name="OutputSchema")
        class_registry.register("OutputSchema", self.output_schema)

    def declare_schema(self):
        pass

    @abstractmethod
    def setup_model(self, pretrained_file_path):
        pass

    @abstractmethod
    def infer(self, json_input):
        pass