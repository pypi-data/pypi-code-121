
"""
    Json Settings Read / Write
"""

import json
class JsonReadWrite:
    """
        - Read settings file from json format and return it
        - Write in any settings that are blank with option to save to file
        - Write out json file if file is missing
            - values
                - string, int, float
                - [list], {"dict":"value"}
    """

    def __init__(self,filename,allowempty:bool=True,writeblank:bool=True) -> None:
        self.json_data = None
        self.writeblank = writeblank
        self.filename = filename
        self.allowempty = allowempty
        self.settings = {}
        self._loadjson()

    def _tryjson(self,value):
        """
            Try to convert value to json
        """
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
        return value 
    
    def _savesettings(self):
        """
            Save settings to json file
        """
        with open(self.filename, "w",encoding='utf-8') as file:
            json.dump(self.settings,file,indent=6)

    def _loadjson(self):
        """
            Load json file
        """
        try:
            with open(self.filename, "r",encoding='utf-8') as file:
                self.settings = json.loads(file.read())
                change = False
                if self.allowempty is False:
                    for check in self.settings:
                        if self.settings[check] == "":
                            self.settings[check] = self._tryjson(input(f"Please input value for {check}: "))
                            change = True
                    if change:
                        answer = input("Do you want to save the changes to file? (y/n) ").casefold()
                        if answer == "y":
                            self._savesettings()
                return self.settings

        except FileNotFoundError:
            if self.writeblank:
                self._savesettings()
            else:
                print(f"{self.filename} not found please create it or follow along to fill it.")
                print("type .exit as key to exit or .save to save file and read settings")
                print('value can be a number, string, float, [list], {"dict":"value"} \n')
                while True:
                    key = input("Please write in the Key: ")
                    if key == ".exit":
                        exit()
                    if key == ".save":
                        self._savesettings()
                        return self._loadjson()
                    value = self._tryjson(input("Please write the Value: "))
                    self.settings[key] = value
                    print(json.dumps(self.settings,indent=6))
        except json.JSONDecodeError:
            print(f"{self.filename} is an invalid json file")
            exit()
    
    def get(self,key):
        """
            Get value from settings
        """
        try:
            return self.settings[key]
        except KeyError:
            return None
    
    def set(self,key,value):
        """
            Set value in settings
        """
        self.settings[key] = value
        self._savesettings()