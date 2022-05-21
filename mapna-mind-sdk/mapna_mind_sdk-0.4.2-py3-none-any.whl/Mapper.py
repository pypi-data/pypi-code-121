import json
from mapnamindsdk.Rest import Rest
from mapnamindsdk import Constants


class Mapper:
    __instance = None

    SignalMapper = None

    def __init__(self,plant):
        """ Virtually private constructor. """
        if Mapper.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.plant = plant
            Mapper.SignalMapper = Mapper.getMapper(plant)
            Mapper.__instance = self


    @staticmethod
    def getInstance(plant):

        if Mapper.__instance == None:
            Mapper(plant)
        return Mapper.__instance

    @staticmethod
    def getMapper(plant):
        try:
            request = Rest(
                f'http://{Constants.GATEWAY_SERVER_IP}:{Constants.GATEWAY_PORT_MAPPER}', path='/getmapper')
            dictResponse = request.get(get_json=True)
            # print(dictResponse)
            dictResult = {}
            for signal in dictResponse:
                if dictResponse[signal]['plantId'] == plant:
                    dictResult[dictResponse[signal]['signalName']] = signal
            # print(dictResult)
        except Exception as e:
            print(str(e))
            return None
        return dictResult