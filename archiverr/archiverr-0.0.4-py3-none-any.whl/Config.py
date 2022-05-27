'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : Config.py
    Classe Config : 
        Classe qui permet de gérer le fichier de configuration
'''
from configparser import ConfigParser

import src.Constants as Constants
from os import path, getcwd
class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.configFile = Constants.NAME_OF_CONFIG_FILE
        # if the getcwd end with "flask_app"
        # then we are in the flask_app folder
        # and we need to go up one level
        if getcwd().endswith("flask_app"):
            # remove the last two folders
            self.configPath = getcwd()[:-13] + self.configFile
        else:
            self.configPath = getcwd() +"/"+self.configFile
        
        if not path.isfile(self.configPath):
            self.__initSectionsAndOptions()

        self.config.read(self.configPath)
        pass

    def getOption(self, section, option):
        return self.config.get(section, option)
    
    def setOption(self, section, option, value):
        self.config.set(section, option, value)
        self.__updateConfig()
        pass

    def __initSectionsAndOptions(self):
        for section in Constants.DICT_OF_CONFIG_SECTIONS:
            if not self.config.has_section(section):
                self.__addSection(section)
            for option in Constants.DICT_OF_CONFIG_SECTIONS[section]:
                if not self.config.has_option(section, option):
                    self.setOption(section, option, Constants.DICT_OF_CONFIG_SECTIONS[section][option])
        self.__updateConfig()
        
        pass

    def __addSection(self, section):
        self.config.add_section(section)
        pass

    def __updateConfig(self):
        with open(self.configPath, 'w') as configfile:
            self.config.write(configfile)
        self.config.read(Constants.NAME_OF_CONFIG_FILE)
        pass