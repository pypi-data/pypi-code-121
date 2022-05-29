######################################################
## si@medatechuk.com
## 12/09/21
## https://github.com/MedatechUK/Medatech.APY
##
## Load configuration file containg settings for the 
## loading. This may be either the IIS web.config or
## from a file called constants.py in the root dir.
##
## Example constant.py:
#    oDataHost ="walrus.ntsa.uk"
#    tabulaini ="tabula.ini"
#    ouser ="apiuser"
#    opass ="123456"
#    Environment = "wlnd"

import os, json
import xmltodict
import inspect
from MedatechUK.mLog import mLog

class Config:
    
    ## Ctor
    def __init__(self, **kwargs): 

        ## Register for log
        self.log = mLog()    
        
        ## Init Vars
        self.config = {}
        self.oDataHost = ''
        self.tabulaini = ''
        self.ouser = ''
        self.opass = '' 
        self.path = ""       
        self.connstr = 'Server=localhost\PRI,1433;Trusted_Connection=Yes;MultipleActiveResultSets=true;'  
        
        ## Set the environment (Priority Company)
        self.environment = ""
        for arg in kwargs.keys():
            ## If it's a request then take the environment 
            #  from the request object
            if arg == 'request' :    
                self.path = kwargs[arg].path
                self.environment = kwargs[arg].environment

                ## Try the web.config first
                if os.path.isfile(self.path + "\web.config"):
                    self.SettingfromWebConfig()
                elif os.path.isfile(self.path + "\constants.py"):
                    self.SettingfromConstants()
                else:
                    self.log.logger.critical("No settings found in [{}].".format( self.path ))
                    raise

            ## If there's no request (i.e. not a web integration) 
            #  use the odata environment
            if arg == 'env':         
                self.path = kwargs['path']
                self.environment = kwargs[arg]
                ## Try the constants.py first
                if os.path.isfile(self.path + "\constants.py"):
                    self.SettingfromConstants()
                elif os.path.isfile(self.path + "\web.config"):
                    self.SettingfromWebConfig()
                else:
                    self.log.logger.critical("No settings found in [{}].".format( self.path ))
                    raise

    ## Load setting from the IIS web.config                    
    def SettingfromWebConfig(self):
        ## Load the config file
        self.log.logger.debug("Opening [{}].".format( self.path + '\web.config' ))
        with open(self.path + '\web.config') as fd:  
            self.config = xmltodict.parse(fd.read(), process_namespaces=True)    

        ## Get the oData settings from the web.config
        for k in self.config['configuration']['appSettings']['add']:
            if k['@key'].upper() == 'ODATAHOST':
                self.oDataHost = k['@value'].split("//")[1]
            if k['@key'].upper() == 'TABULAINI':
                self.tabulaini = k['@value']
            if k['@key'].upper() == 'OUSER':
                self.ouser = k['@value']
            if k['@key'].upper() == 'OPASS':
                self.opass = k['@value']                  
        
        ## Get the Priority Database connection string from the web.config
        if str(type(self.config['configuration']['connectionStrings']['add'])) =="<class 'list'>":
            for k in self.config['configuration']['connectionStrings']['add']:                                    
                if k['@name'].upper() == 'PRIORITY':
                    self.connstr = k['@connectionString']
        if str(type(self.config['configuration']['connectionStrings']['add'])) =="<class 'collections.OrderedDict'>":                            
            if self.config['configuration']['connectionStrings']['add']['@name'].upper() == 'PRIORITY':
                self.connstr = self.config['configuration']['connectionStrings']['add']['@connectionString']  

    ## Load settings from file constanst.py
    def SettingfromConstants(self):                
        ## Load the constants file
        self.log.logger.debug("Opening [{}].".format( self.path + '\constants.py' ))
        Lines = {}
        with open(self.path + '\constants.py') as fd:  
            Lines = fd.readlines()
        for line in Lines:
            if line.find("=") > -1:
                if 'ODATAHOST' in line.split("=")[0].upper():
                    self.oDataHost = line.split("=")[1].split('"')[1]            
                if 'TABULAINI' in line.split("=")[0].upper():
                    self.tabulaini = line.split("=")[1].split('"')[1]
                if 'OUSER' in line.split("=")[0].upper():
                    self.ouser = line.split("=")[1].split('"')[1]
                if 'OPASS' in line.split("=")[0].upper():
                    self.opass = line.split("=")[1].split('"')[1]                                