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

    def createVersionFile(self,version:float) -> bool:
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
        if os.path.exists(f"{self.__path}\\version.json"):
            with open(f"{self.__path}\\version.json","rb") as g:
                data = json.load(g)["version"]
                if float(data) < float(self.get_version["version"]):
                    return False

                elif float(data) == float(self.get_version["version"]):
                    return True
                
                else:
                    raise LogicError()
        else:
            raise VersionFileNotFound("Create version.json first!")
    
    def downloadLink(self,url:str) -> None:
        """
            The argument given to the PyDate class is used as the path.
            Creates a folder named "Installed"

            :param url: Downloadlink of current program/file/exe available on Github.     
        """
        if self.downloaded_name.count(".") > 1:
            raise TypeError("There is no such extension")
        else:
            if not os.path.exists(f"{os.getcwd()}\\Installed"):
                os.mkdir(f"{self.__path}\\Installed")
                resp = requests.get(url,allow_redirects=True)
                with open(f"{self.__path}\\Installed\\{self.downloaded_name}","wb") as file:
                    file.write(resp.content)
    
    @property
    def downloaded_name(self):
        "Value by adding an extension to the end of the name"
        return self.__name

    @downloaded_name.setter
    def downloaded_name(self,name:str) -> None:
        self.__name = name
        return self.__name

    def openNewVersion(self):
        "Opens the downloaded file in the `Installed` folder and upgrades the `version.json` version."
        __file = f"{os.getcwd()}\\Installed\\{self.downloaded_name}"
        if os.path.exists(__file):
            with open(f"{self.__path}\\version.json","w") as g:
                json.dump({"version":self.get_version["version"]},g)
            os.startfile(__file)
        else:
            raise FileNotFoundError("File 'Installed' does not exist")