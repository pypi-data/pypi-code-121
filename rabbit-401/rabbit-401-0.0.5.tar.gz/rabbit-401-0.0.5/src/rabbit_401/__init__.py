from bson.objectid import ObjectId



class Rabbit401:
    def __init__(self):
        self.full_data = {}

    def insertItem(self, value, key=None):
        if key == None:
            key = str(ObjectId())

        self.full_data[key] = value
        return key

    def deleteItem(self, key):
        try:
            item_value = self.full_data.pop(key)
            return item_value
        except:
            return None


    def getItem(self, key):
        item_value = self.full_data.get(key)
        return item_value