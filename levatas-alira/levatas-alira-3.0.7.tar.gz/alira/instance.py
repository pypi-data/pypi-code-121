import uuid
import jmespath

class Instance(object):
    def __init__(
        self,
        id: str = None,
        prediction: int = None,
        confidence: float = None,
        files: list = None,
        metadata: dict = None,
        properties: dict = None,
    ) -> None:
        self.id = id or uuid.uuid4().hex
        self.prediction = prediction
        self.confidence = confidence
        self.files = files

        if self.files and not isinstance(self.files, list):
            self.files = [self.files]

        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("The field 'metadata' must be a dictionary.")

        self.metadata = metadata or {}
        self.properties = properties or {}

    def has_attribute(self, name: str):
        try:
            self.get_attribute(name)
            return True
        except AttributeError:
            return False

    def get_attribute(self, name: str, *arg, **kwargs):
        def raise_exception(name: str, value):
            raise AttributeError(f"The attribute '{name}' does not exist.")

        def default_value(name, value):
            return value

        value = None
        attribute_doesnt_exist = raise_exception
        if "default" in kwargs:
            attribute_doesnt_exist = default_value
            value = kwargs["default"]
        elif len(arg) == 1:
            attribute_doesnt_exist = default_value
            value = arg[0]

        if name is None:
            return attribute_doesnt_exist(name, value)

        expression = jmespath.search(name, self.to_dict())
        if expression is None:
            return attribute_doesnt_exist(name, value)

        return expression

    def to_dict(self):
        result = self.__dict__.copy()

        # Remove the private attribute representing the image
        # and add the value of the property.
        if "_Instance__image" in result:
            del result["_Instance__image"]

        return result

    @staticmethod
    def create(data):
        data = data.copy()

        id = data.get("id", None)
        prediction = data.get("prediction", None)
        confidence = data.get("confidence", None)
        files = data.get("files", None)

        if "id" in data:
            del data["id"]

        if "prediction" in data:
            del data["prediction"]

        if "confidence" in data:
            del data["confidence"]

        if "files" in data:
            del data["files"]

        if "metadata" in data:
            metadata = data["metadata"]
            del data["metadata"]
        else:
            metadata = {}

        if "properties" in data:
            properties = data["properties"]
            del data["properties"]
        else:
            properties = {}

        for key, value in data.items():
            metadata[key] = value

        instance = Instance(
            id=id,
            prediction=prediction,
            confidence=confidence,
            files=files,
            metadata=metadata,
            properties=properties,
        )

        return instance

    @staticmethod
    def _format(data: dict) -> dict:
        for key, value in data.items():
            data[key] = value

        return data


def onlyPositiveInstances(instance: Instance):
    return instance.prediction == 1


def onlyNegativeInstances(instance: Instance):
    return instance.prediction == 0
