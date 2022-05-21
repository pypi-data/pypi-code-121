import pickle

class Serializable:
    '''serializing and deserializing objects in binary files'''

    def __init__(self, file_name):
        self.file_name = file_name

    def serialize(self, obj):
        with open(self.file_name, "wb") as fb:
            pickle.dump(obj, fb)

    def deserialize(self):
        with open(self.file_name, "rb") as fb:
            return pickle.load(fb)