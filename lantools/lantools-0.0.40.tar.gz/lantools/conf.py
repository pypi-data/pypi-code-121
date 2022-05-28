from configparser import ConfigParser

class MyConfig:
    def __init__(self, filename):
        self.parser = ConfigParser()
        self.parser.read(filename)

        self.buffer = self._load()

    def _load(self):
        result = {}
        for section in self.parser.sections():
            temp = {}
            for option in self.parser.options(section):
                name,value=self._get(section, option)
                #print(section, option, name, value)
                temp[name] = value

            result[section] = temp
        return result

    def get(self, section, option=None):
        if option==None:
            return self.buffer[section]
        else:
            return self.buffer[section][option]

    def _get(self, section, option):
        val = self.parser.get(section, option)
        arr = option.split('.')
        #print(option.split('.'))
        if len(arr)==1:
            return arr[0],val
        elif arr[-1]=='array':
            return arr[0],[_convert(item, arr[:-1]) for item in val.split(',')]
        else:
            return arr[0],_convert(val, arr)

def _convert(value, setting):
    if len(setting)==1:
        return value
    else:
        modifier = setting[-1]
        #print(setting, modifier)
        if modifier=='int':
            return int(value)
        elif modifier=='float':
            return float(value)
        elif modifier=='bool':
            return bool(int(value))
        else:
            return value

def read_conf(file) -> MyConfig:
    return MyConfig(file)
