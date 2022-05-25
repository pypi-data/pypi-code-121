from .Exceptions import *
import os
import requests
import json

class PyDate:
    def __init__(self,path:str,rawlink:str) -> None:
        """
        :param `path`: Location of local version file
        :param `rawlink`: Here is the `raw link` of the latest version number on github
        """
        self.__path = path
        self.__rawlink = rawlink
        self.__version = ""
        self.__read = None

    def create_version_file(self,version:float) -> bool:
        """ 
        If the version file does not exist, it will create it.
        The resulting file is a `json` file.
        
        Returns `False` if the version file exists.
        Returns `True` if the version file does not exist.
        :param version: `float` accepts a value.
        """
        if type(version) is not float:
            raise TypeError("Float value is required!")

        if not os.path.isdir(self.__path):
            raise PathIsEmpty()

        if not os.path.exists(f"{self.__path}\\version.json"):
            with open(f"{self.__path}\\version.json","w") as f:
                json.dump({'version':f"{version}"},f)
            return True
        else:
            return False
    
    @property
    def get_version(self) -> dict:
        " Returns version file written on github"
        r = requests.get(self.__rawlink)
        self.__version = r.content.decode()
        self.__read = json.loads(self.__version)
        return self.__read
    
    @property
    def isUpdate(self) -> bool:
        " Returns `True` if Current, `False` if Not Current "
        with open(f"{self.__path}\\version.json","rb") as g:
            data = json.load(g)["version"]
            if float(data) < float(self.get_version["version"]):
                return False

            elif float(data) == float(self.get_version["version"]):
                return True
            
            else:
                raise LogicError()
    
    def writeNewVersion(self) -> None:
        """Value of the `version` key in the version.json file on Github
            rewrites it by changing the value of the `version` key in the generated version.json.
        """
        with open(f"{self.__path}\\version.json","w") as g:
            json.dump({"version":self.get_version["version"]},g)
    
    def downloadLink(self,url:str,extension:str) -> None:
        """
            :param url: Downloadlink of current program/file/exe available on Github
            :param extension: File extension of the file to be downloaded
             >>> extension = ".json",".exe",".pdf", ...       
        """
        if extension.startswith("."):
            if extension.count(".") > 1:
                raise TypeError("There is no such extension")
            else:
                resp = requests.get(url,allow_redirects=True)
                with open(f"{self.__path}\\NowDownload{extension}","wb") as file:
                    file.write(resp.content)
        else:
            raise TypeError("There is no such extension")
    
