from google.protobuf.json_format import MessageToDict
from jarvis_sdk.utils.message_to_value import object_to_value


class Property:
    @classmethod
    def deserialize(cls, message):
        dict_message = MessageToDict(message)
        value = None
        if 'referenceValue' in dict_message:
            value = dict_message['referenceValue']
        elif 'objectValue' in dict_message:
            value = object_to_value(message.object_value)
        return Property(
          dict_message['id'],
          dict_message['definition']['property'],
          dict_message['meta'],
          value
        )

    def __init__(self, prop_id, prop, meta, value):
        self.id = prop_id
        self.property = prop
        self.meta = meta
        self.value = value

    def __str__(self):
        return (
            "Property: " + self.property + "\n"
            "ID: " + self.id + "\n"
            "Value: " + str(self.value) + "\n"
        )
