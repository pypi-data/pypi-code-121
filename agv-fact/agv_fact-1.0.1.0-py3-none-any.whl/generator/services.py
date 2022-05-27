from fact.generator.generator33 import GeneratorXmlThreeDotThree
from fact.generator.generator40 import GeneratorXmlFourDotZero


class GeneratorService:

    def __init__(self, data):
        self.__generator = None
        if data.get('version') == '3.3':
            self.__generator = GeneratorXmlThreeDotThree(data)
        elif data.get('version') == '4.0':
            self.__generator = GeneratorXmlFourDotZero(data)

    def generator(self):
        return self.__generator
