class ArraysDict(dict):
    def add(self,key,value):
        if not dict.__contains__(self, key):
            dict.__setitem__(self, key, [])
        values = dict.__getitem__(self, key)
        values.append(value)
        return dict.__setitem__(self, key, values)

    def keys(self):
        return list(super().keys())

    def values(self):
        return list(super().values()) 