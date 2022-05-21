import cherrypy
from threading import Thread

from mapnamindsdk import WS as WS
from mapnamindsdk.Rest import Rest
from dist.Mind import Mind
import mapnamindsdk.Constants as Constants


class Online(Mind):

    @staticmethod
    def _startWS():
        cherrypy.quickstart(WS.MindSdkWebService)

    @staticmethod
    def startWS():
        Thread(target=Online._startWS).start()

    @staticmethod
    def callback():
        print("finished!")

    @staticmethod
    def set(key, value):
        WS.MindSdkWebService.set(key=key, value=value)

    @staticmethod
    def add(key, value):
        WS.MindSdkWebService.add(key=key, value=value)

    @staticmethod
    def getResult(key):
        return WS.MindSdkWebService.getResult(key)

    @staticmethod
    def getResultList(key):
        return WS.MindSdkWebService.getList(key)

    @staticmethod
    def getValue(signalNames, startDate, endDate, userId):

        Mind._validate(startDate)
        Mind._validate(endDate)

        try:
            body = {"signalNames": signalNames,
                    "startTime": startDate,
                    "endTime": endDate,
                    "userId": userId
                    }

            request = Rest(f'http://{Constants.GATEWAY_SERVER_IP}:{Constants.GATEWAY_PORT}', path='/sdk/online/get', params=body)
            jsonResult = request.post(get_json=True)

            return jsonResult

        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        return None


if __name__ == "__main__":
    params = {'par1': 'value1', 'par2': 3}

    req = Rest(base_url='https://postman-echo.com',
               path='/get', params=params)

    post_req = Rest(base_url='https://postman-echo.com',
                    path='/post', params=params)

    # print(post_req.do_it('POST'))

#     print(req.get())
    print(req.get())