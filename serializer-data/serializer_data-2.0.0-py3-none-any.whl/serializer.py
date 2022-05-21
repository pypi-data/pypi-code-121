import pickle

class Serializer:
    '''serializing and deserializing objects in binary files,
       all methods are static'''

    def __init__(self):
        pass

    def serialize(obj, file_name):
        with open(file_name, "wb") as fb:
            pickle.dump(obj, fb)

    def deserialize(file_name):
        with open(file_name, "rb") as fb:
            return pickle.load(fb)