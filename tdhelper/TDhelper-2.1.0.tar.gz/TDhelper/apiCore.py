import urllib.request
import io
import os
import json
from TDhelper.bin.globalvar import *
from TDhelper.network.http.REST_HTTP import GET, POST


class apiCore():
    '''apiCore

       Args:
            apiName (str):Open Api platform's Name.
            version (str):Api's version, default value is "v1".
            apiRouteFileName (str):Location cache file's name, default value is "apiRoutePath"
            basePath (str):Location cache base path, defalut value is os.path.dirname(__file__)
    '''

    def __init__(self, apiName: str, version="v1", apiRouteFileName="apiRoutePath.arg", basePath=os.path.dirname(__file__)):
        self._apiName = apiName+"_"+version
        self._path = basePath+"\\"+apiName+"\\"+version+"\\"
        # if haven't this directory,create it.
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        # generate the api route path
        self._routePath = os.path.join(self._path, apiRouteFileName)
        if not hasKey(apiName+version):
            # create global route tables
            setGlobalVariable(self._apiName, dict())
        if self._routePath:
            if os.path.exists(self._routePath):
                # read apiRouteFile and init apiroute
                try:
                    with open(self._routePath, mode='r', encoding='utf-8', errors=None, newline=None) as f:
                        while True:
                            line = f.readline().replace("\n", "")
                            if line:
                                jsondoc = json.loads(line)
                                if jsondoc["key"]:
                                    if jsondoc["value"]:
                                        self.AddApi(jsondoc["key"], jsondoc["value"]["uri"], jsondoc["value"]
                                                    ["args"], jsondoc["value"]["method"], jsondoc["value"]["descrition"])
                            else:
                                break
                        f.close()
                except Exception as e:
                    raise e

    def AddApi(self, key: str, apiUri: str, argsStr: str, method: str = "GET", descrition: str = ""):
        '''Add a new api

            Args:
                key (str): Api key.
                apiUri (str): Api uri.
                argsStr (str): Api uri args string format, Example: "gid={0}&name={1}".
                method (str): Http method, default value is "GET".
                descrition (str): api descrition.
        '''
        # if key.lower() not in self._apiRoute:
        if key.lower() not in getGlobalVariable(self._apiName):
            getGlobalVariable(self._apiName)[key.lower()] = {
                "uri": apiUri, "args": argsStr, "method": method.lower(), "descrition": descrition}
            return True
        else:
            return False

    def GetArgsString(self, key: str):
        '''Get api uri's param string

            Args:
                key (str): api key
        '''
        try:
            key = key.lower()
            if key in getGlobalVariable(self._apiName):
                if "args" in getGlobalVariable(self._apiName)[key]:
                    return getGlobalVariable(self._apiName)[key]["args"]
        except Exception as e:
            raise e

    def DelApi(self, key: str):
        '''Delete a api

            Args:
                key (str): api key
        '''
        key = key.lower()
        if key in getGlobalVariable(self._apiName):
            del getGlobalVariable(self._apiName)[key]
            return True
        else:
            return False

    def SaveToFile(self):
        '''Save api route to file
        '''
        wBuffer = ""  # create file write buffer
        for item in getGlobalVariable(self._apiName):
            wBuffer += json.dumps({"key": item,
                                   "value": getGlobalVariable(self._apiName)[item]})+"\r\n"
        if not wBuffer:
            wBuffer = "\r\n"
        if wBuffer:  # save buffer to file
            with open(self._routePath, mode='w', encoding='utf-8', errors=None, newline=None) as f:
                f.write(wBuffer)
                f.flush()
                f.close()

    def ClearCache(self):
        deleteGlobalVariable(self._apiName)  # 删除全局变量
        os.remove(self._routePath)  # 删除缓存文件
        os.removedirs(self._path)  # 删除缓存目录

    def Call(self, key: str, data: str):
        '''Call remote api

            Args:
                key (str): api key.
                data (str): api uri's params string.
        '''
        key = key.lower()
        if key in getGlobalVariable(self._apiName):
            method = getGlobalVariable(self._apiName)[key]["method"]
            uri = getGlobalVariable(self._apiName)[key]["uri"]
            if uri:
                if method.lower() == "get":
                    uri += "?"+data
                    return self._restfulGET(uri)
                elif method.low() == "post":
                    return self._restfulPOST(uri, data)
            return False
        return False
    def _restfulGET(self, uri):
        try:
            return GET(uri)
        except Exception as e:
            raise e

    def _restfulPOST(self, uri, data):
        try:
            return POST(uri, data)
        except Exception as e:
            raise e
