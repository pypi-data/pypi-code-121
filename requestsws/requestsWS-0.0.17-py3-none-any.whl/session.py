from websocket import create_connection
from requestsWS import misc
import json as JSON

import threading
from cancelable import time
import timeout_decorator

class formatCorrectly:
    def __init__(self, text=None, status_code=None):
        self.text = text
        self.status_code = status_code

    def json(self):
        return JSON.loads(self.text)

class _get:
    def __init__(self, ws, wsUrl, wsData, headers={}, encryption=None, identifiers=None, timeout=None, debug=False):
        if wsUrl != wsData["CURRENT_URL"]:
            wsData["CURRENT_URL"] = wsUrl
            ws = create_connection(wsUrl, header=headers, enable_multithread=True)

        keys = []
        values = []
        if identifiers != None:
            for i in range(len(identifiers)):
                key, value = identifiers.popitem()
                keys.append(key)
                values.append(value)


        #@timeout_decorator.timeout(timeout if timeout != 0 else 10**-100) | Removed for now as it causes problems
        def funcWaitForResponse(identifiers):
            if debug:
                while True:
                    response = misc.decompress(ws.recv(), encryption)
                    print(response)
            while True:
                response = misc.decompress(ws.recv(), encryption)
                if response:
                    if identifiers != None:
                        identifiersInIt = True
                        for i in range(len(keys)):
                            try:
                                if JSON.loads(response)[keys[i]] == values[i] and identifiersInIt:
                                    identifiersInIt = True
                                else:
                                    identifiersInIt = False
                            except Exception:
                                identifiersInIt = False
                        if identifiersInIt:
                            return response
                    else:
                        return response
        self.text = funcWaitForResponse(identifiers)
        self.status_code = 200

        self.ws = ws
        self.wsData = wsData

class _post:
    def __init__(self, ws, wsUrl, wsData, headers={}, encryption=None, data=None, json=None, waitForResponse=True, identifiers=None, timeout=None, debug=False):
        if data == None and json == None:
            exit("RequestsWS | Error #1: Data or json is needed")

        if wsUrl != wsData["CURRENT_URL"]:
            wsData["CURRENT_URL"] = wsUrl
            ws = create_connection(wsUrl, header=headers, enable_multithread=True)

        dataFormatted = JSON.dumps(data) if type(data) == dict else data if data != None else JSON.dumps(json)
        ws.send(dataFormatted)
        self.status_code = 200

        keys = []
        values = []
        if identifiers != None:
            for i in range(len(identifiers)):
                key, value = identifiers.popitem()
                keys.append(key)
                values.append(value)


        #@timeout_decorator.timeout(timeout if timeout != 0 else 10**-100) | Removed for now as it causes problems
        def funcWaitForResponse(identifiers):
            if debug:
                while True:
                    response = misc.decompress(ws.recv(), encryption)
                    print(response)
            while True:
                response = misc.decompress(ws.recv(), encryption)
                if response:
                    if identifiers != None:
                        identifiersInIt = True
                        for i in range(len(keys)):
                            try:
                                if JSON.loads(response)[keys[i]] == values[i] and identifiersInIt:
                                    identifiersInIt = True
                                else:
                                    identifiersInIt = False
                            except Exception:
                                identifiersInIt = False
                        if identifiersInIt:
                            return response
                    else:
                        return response

        if waitForResponse:
            self.text = funcWaitForResponse(identifiers)

        self.ws = ws
        self.wsData = wsData

class Session:
    def __init__(self, proxies=None, timeout=None):
        self.ws = None
        self.wsData = {"CURRENT_URL": None}

        self.connectionsKept = []

    def get(self, wsUrl, headers={}, encryption=None, identifiers=None, timeout=None, debug=False):
        resp = _get(ws=self.ws, wsUrl=wsUrl, wsData=self.wsData, headers=headers, encryption=encryption, identifiers=identifiers, timeout=timeout, debug=debug)
        self.ws = resp.ws
        self.wsData = resp.wsData

        return formatCorrectly(resp.text, resp.status_code)

    def post(self, wsUrl, headers={}, encryption=None, data=None, json=None, waitForResponse=True, identifiers=None, timeout=None, debug=False):
        resp = _post(ws=self.ws, wsUrl=wsUrl, wsData=self.wsData, headers=headers, encryption=encryption, data=data, json=json, waitForResponse=waitForResponse, identifiers=identifiers, timeout=timeout, debug=debug)
        self.ws = resp.ws
        self.wsData = resp.wsData

        if waitForResponse:
            return formatCorrectly(resp.text, resp.status_code)

    def isRunning(self, wsUrl):
        if wsUrl in self.connectionsKept:
            return True
        return False

    def heartbeat(self, wsUrl, interval, payload):
        time.sleep(interval)
        while self.isRunning(wsUrl):
            self.ws.send(payload)
            time.sleep(interval)

    def keepConnection(self, wsUrl, interval, data=None, json=None):
        if data == None and json == None:
            exit("RequestsWS | Error #1: Data or json is needed")

        dataFormatted = JSON.dumps(data) if type(data) == dict else data if data != None else JSON.dumps(json)
        self.connectionsKept.append(wsUrl)
        threading._start_new_thread(self.heartbeat, (wsUrl, interval, dataFormatted))

    def closeConnection(self, wsUrl):
        self.wsData["CURRENT_URL"] = None
        try:
            self.connectionsKept.remove(wsUrl)
        except Exception:
            pass
        time.cancel()
        self.ws.close()
