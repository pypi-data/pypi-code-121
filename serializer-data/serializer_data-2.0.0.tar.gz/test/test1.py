import sys
sys.path.insert(1, "C:/Users/asus/OneDrive/Desktop/Serializer")
from serializer_data.serializer import Serializer

data_set = {"key1": 3, "key2": 5}

serial = Serializer.serialize(data_set, "fileBinary.mm")

new_data_set = Serializer.deserialize("fileBinary.mm")

print(new_data_set)