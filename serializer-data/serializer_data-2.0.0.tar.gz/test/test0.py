import sys
sys.path.insert(1, "C:/Users/asus/OneDrive/Desktop/Serializer")
from serializer_data.serializable import Serializable

data_set = {"key1": 3, "key2": 5}

serial = Serializable("fileBinary.mm")

serial.serialize(data_set)

new_data_set = serial.deserialize()

print(new_data_set)