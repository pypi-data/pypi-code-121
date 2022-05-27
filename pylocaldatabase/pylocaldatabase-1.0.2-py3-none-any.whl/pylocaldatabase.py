
import json
import hashlib


class item():
    __data = {}
    __name = ""

    def getName(self):
        return self.__name

    def get(self):
        return self.__data

    def setData(self, data):
        self.__data = data

    def __init__(self, data, name):
        self.__data = data
        self.__name = name

    def insertProperty(self, name, value):
        self.__data[name] = value

    def hash(self):
        return databaseDocument.getHash(self)


class databaseDocument(object):

    def __dictKeysToList__(self, dict):
        _list = []
        for x in dict:
            _list.append(x)
        _list.sort()
        return _list

    def __dictToList__(self, dict):
        _list = []
        for x in dict:
            if(type(dict[x]) == str):
                _list.append(dict[x].getName())
        _list.sort()
        return _list

    def binarySearch(self, array, value):
        mid = array[len(array)//2]
        try:
            if mid == value:
                return 1
            elif value < mid:
                return self.binarySearch(array[:len(array)//2], value)
            elif value > mid:
                return self.binarySearch(array[len(array)//2:], value)
        except:
            return 0

    def __doKeyBinarySearch__(self, value):
        if(len(self.__data) > 1):
            return 0 != self.binarySearch(self.__dictKeysToList__(self.__data), value)
        else:
            print("A document must be bigger than 1 item to be searchable.")

    def __doValueBinarySearch__(self, value):
        if(len(self.__data) > 1):
            return 0 != self.binarySearch(self.__dictToList__(self.__data), value)
        else:
            print("A document must be bigger than 1 item to be searchable.")

    def __init__(self, data, name):
        self.__data = data
        self.__name = name

    def insertItem(self, name: str, data: dict):
        self.__data[name] = item(data, name)

    def getName(self):
        return self.__name

    def containsKey(self, name) -> bool:
        return self.__doKeyBinarySearch__(name)

    def containsValue(self, name) -> bool:
        """Return true if a string is found in any of the documents."""
        return self.__doValueBinarySearch__(name)

    def set(self, property, data):
        self.__data[property] = data

    def remove(self, property):
        self.__data.pop(property)

    def get(self) -> dict:
        return self.__data

    def getItem(self, name) -> item:
        try:
            return self.__data[name]
        except:
            return item({"Err": True}, "Err")

    def getHash(self) -> hashlib.md5:
        return hashlib.md5((str(json.dumps(self.get(), default=databasecontroller.serialize))).encode('utf-8')).hexdigest()


class databasecontroller:
    __path = ""
    __docs = {}

    def serialize(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, databaseDocument):
            serial = obj.get()
            return serial

        if isinstance(obj, item):
            serial = obj.get()
            return serial

        return obj.__dict__

    def documentExists(self, name) -> bool:
        try:
            data = self.__docs[name]
            return True
        except:
            return False

    def getDocument(self, name: str) -> databaseDocument:
        try:
            return self.__docs[name]
        except:
            return False

    def __init__(self, path):
        self.__path = path

    def makeDatabase(self):
        fs = open(self.__path, "w+")
        fs.close()

    def generateDocuments(self, data):
        for x in data:
            self.__docs[x] = databaseDocument({}, x)
            try:
                for y in data[x]:
                    self.__docs[x].insertItem(y, data[x][y])
            except:
                raise Exception(
                    "Error generating itens for document: " + data[x])

    def insertDocument(self, content, name):
        if(self.documentExists(name) == False):
            data = {}
            print(content)
            for x in content:
                data[x] = item(content[x], x)
            self.__docs[name] = databaseDocument(data, name)
        else:
            raise Exception("Error generating document: " + name +
                            ". document already exists or content couldn't be appended to instances of Item.")

    def getWhere(self, field, value) -> databaseDocument:
        try:
            for x in self.__docs:
                if(self.__docs[x].get()[field] == value):
                    return self.__docs[x]
        except:
            return False

    def load(self):
        try:
            fs = open(self.__path)
            data = json.loads(fs.read())
            fs.close()
            if(data):
                self.generateDocuments(data)
        except:
            raise Exception(
                "File not found or corrupted -> "+self.__path)

    def save(self):
        try:
            pos = 1
            fs = open(self.__path, "w+")
            fs.write('{')
            for x in self.__docs:
                data = self.__docs[x]
                if(pos != len(self.__docs.keys())):
                    fs.write(
                        '"'+x+'":'+json.dumps(data, default=databasecontroller.serialize)+',')
                else:
                    fs.write(
                        '"'+x+'":'+json.dumps(data, default=databasecontroller.serialize))
                pos += 1
            fs.write('}')
            fs.close()
        except:
            raise Exception("Error saving file -> "+self.__path)
