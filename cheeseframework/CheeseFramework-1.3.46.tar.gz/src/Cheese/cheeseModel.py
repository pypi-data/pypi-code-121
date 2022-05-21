#cheese

class CheeseModel:
    
    def __init__(self, modelName, scheme):
        self.modelName = modelName
        self.scheme = scheme

    def toJson(self):
        jsn = {}
        for attr in self.scheme:
            jsn[attr.upper()] = getattr(self, attr)
        return jsn

    def toModel(self, jsn):
        if (type(jsn).__name__ == "dict"):
            for attr in self.scheme:
                if (attr in jsn.keys()):
                    setattr(self, attr, jsn[attr])
                if (attr.upper() in jsn.keys()):
                    setattr(self, attr, jsn[attr.upper()])
        else: #(type(jsn) == list or
            #type(jsn) == tuple):

            for attr, value in zip(self.scheme, jsn):
                setattr(self, attr, value)

    def setAttrs(self, **attrs):
        return self.toModel(attrs)
