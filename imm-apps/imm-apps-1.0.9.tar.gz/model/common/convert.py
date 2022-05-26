"""
This class is for code and name convert. Usually used for country, province,city, etc... to convert between name and code
"""

class NameCodeConvert(object):
    # initialize with a dict including name and code
    def __init__(self,d:dict):
        self.d=d

    def getName(self,code):
        c={v:k for k,v in self.d.items()}
        return c.get(str(code))
    
    def getCode(self,name):
        # remove additional space and trim left and right
        name=' '.join(name.split()).strip()
        for item_name, code in self.d.items():
            if name in item_name.lower():
                return code
#TODO: 此处可以考虑增加模糊选项，如果有错，提供对应的输入建议。 参考noc的输入检查

