from requestsWS.session import Session
from requestsWS import misc
from websocket import create_connection
import json as JSON

import threading
from cancelable import time
import timeout_decorator

ws = None
wsData = {"CURRENT_URL": None}

connectionsKept = []

class get:
    def __init__(self, wsUrl, headers={}, encryption=None, identifiers=None, timeout=None, debug=False):
        global ws
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

    def json(self):
        return JSON.loads(self.text)

class post:
    def __init__(self, wsUrl, headers={}, encryption=None, data=None, json=None, identifiers=None, waitForResponse=True, timeout=None, debug=False):
        global ws

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

    def json(self):
        return JSON.loads(self.text)


def isRunning(wsUrl):
    if wsUrl in connectionsKept:
        return True
    return False

def heartbeat(wsUrl, interval, payload):
    time.sleep(interval)
    while isRunning(wsUrl):
        ws.send(payload)
        time.sleep(interval)

def keepConnection(wsUrl, interval, data=None, json=None):
    if data == None and json == None:
        exit("RequestsWS | Error #1: Data or json is needed")

    dataFormatted = JSON.dumps(data) if type(data) == dict else data if data != None else JSON.dumps(json)
    connectionsKept.append(wsUrl)
    threading._start_new_thread(heartbeat, (wsUrl, interval, dataFormatted))

def closeConnection(wsUrl):
    wsData["CURRENT_URL"] = None
    try:
        connectionsKept.remove(wsUrl)
    except Exception:
        pass
    time.cancel()
    ws.close()
