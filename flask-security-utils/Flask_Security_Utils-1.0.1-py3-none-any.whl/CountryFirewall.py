import logging
import os
from IP2Location import IP2Location, IP2LocationIPTools
from urllib.request import urlopen
from os.path import exists as file_exists

traza = logging.getLogger(__name__)

class CountryFirewall():
    
    """
    Clase de utilidad 
    """
    
    __instance = None
    __ipCountryFileDB = None
    __ipV6CountryFileDB = None
    __databaseIpV4 = None
    __databaseIpV6 = None
    __inMemoryDatabase = None
    __IP2LocationIPTools = None
    
        
    def __new__(cls, ip_country_file_db : str = None,
                ip_v6_country_file_db : str = None,
                blocked_countries  : list = None,
                allowed_countries : list = None,
                in_memory_database : bool = False):
        
        """
        Constructor of the CountryFirewall class.
        """
        
        
        if (cls.__instance == None):
            
            #Register file paths
            cls.__ipCountryFileDB = ip_country_file_db if ip_country_file_db is not None else ""
            cls.__ipV6CountryFileDB = ip_v6_country_file_db if ip_v6_country_file_db is not None else "" 
            cls.__inMemoryDatabase = in_memory_database
            
            #Register country names
            cls.__blockedCountries = blocked_countries
            cls.__allowedCountries = allowed_countries
            
            #Verify before initialize the class
            cls.__verifyCountriesLists(cls)
            
            #Load or download files
            cls.__loadOrDownloadDatabase(cls)
            
            #Create the ip tools object
            cls.__IP2LocationIPTools = IP2LocationIPTools()
                        
            #Create the class
            cls.__instance = object.__new__(cls)
        
        return cls.__instance
    
    def __verifyCountriesLists(cls):
        """
        This function raise an exception when one or more countries are allowed and blocked at the same time.
        """
        
        if None not in [cls.__blockedCountries,cls.__allowedCountries]:
            
            setBlockedList = set(cls.__blockedCountries)
            setAllowedList = set(cls.__allowedCountries)
            intersec = setBlockedList.intersection(setAllowedList)
            
            if len(intersec) > 0:
                raise Exception("The 'BLOCKED_COUNTRIES' and 'ALLOWED_COUNTRIES' contains this repeated countries {}.".format(intersec))
        
    
    def __loadOrDownloadDatabase(cls):
        """
        This function download the database from the git repository if the path doesn't exist.
        """
        
        #Create database folder if it doesn't exist.
        def createFolder():
            if not os.path.exists("ip_database"):
                os.mkdir("ip_database")
    
        #Download IPV4 database if it needed
        if file_exists(cls.__ipCountryFileDB) == False:
            urlIpV4 = "https://github.com/alejivo/Flask-Security-Utils/raw/main/IP2LocationDB/IP2LOCATION-LITE-DB1.BIN"
            createFolder()
            #cls.__downloadFile(cls,url=urlIpV4,filePath=os.path.join("ip_database","IP2LOCATION-LITE-DB1.BIN"))
            cls.__downloadFile(cls,url=urlIpV4,filePath=os.path.join("ip_database","IP2LOCATION-LITE-DB1.BIN"))
            cls.__ipCountryFileDB = os.path.join("ip_database","IP2LOCATION-LITE-DB1.BIN")
        
        #Download IPV6 database if it needed  
        if file_exists(cls.__ipV6CountryFileDB) == False:
            urlIpV6 = "https://github.com/alejivo/Flask-Security-Utils/raw/main/IP2LocationDB/IP2LOCATION-LITE-DB1.IPV6.BIN"
            createFolder()
            cls.__downloadFile(cls, url=urlIpV6, filePath=os.path.join("ip_database","IP2LOCATION-LITE-DB1.IPV6.BIN"))
            cls.__ipV6CountryFileDB = os.path.join("ip_database","IP2LOCATION-LITE-DB1.IPV6.BIN")

        #Load database files
        if cls.__inMemoryDatabase == True:
            cls.__databaseIpV4 : IP2Location = IP2Location(os.path.join("ip_database", "IP2LOCATION-LITE-DB1.BIN"), "SHARED_MEMORY")
            cls.__databaseIpV6 : IP2Location = IP2Location(os.path.join("ip_database", "IP2LOCATION-LITE-DB1.IPV6.BIN"), "SHARED_MEMORY")
        else:
            cls.__databaseIpV4 : IP2Location = IP2Location(os.path.join("ip_database", "IP2LOCATION-LITE-DB1.BIN"))
            cls.__databaseIpV6 : IP2Location = IP2Location(os.path.join("ip_database", "IP2LOCATION-LITE-DB1.IPV6.BIN"))

    
    def isIPInBlockedCountry(cls, ip : str) -> bool:
        """
        This function return True if the IP is into the blocked list, or false if not.
        """
        
        if cls.__IP2LocationIPTools.is_ipv4(ip=ip):
            
            if str(cls.__databaseIpV4.get_country_short(ip)) in cls.__blockedCountries:
                return True
            else:
                return False
        
        elif cls.__IP2LocationIPTools.is_ipv6(ip=ip):
            
            if str(cls.__databaseIpV6.get_country_short(ip)) in cls.__blockedCountries:
                return True
            else:
                return False
            
        else:
            traza.error("The IP[{}] is not ip4 or ip6 and can't be possessed, isIPInBlockedCountry returns False.".format(ip))
            return False
        
    
    def isIPInAllowedCountry(cls, ip : str) -> bool:
        """
        This function return True if the IP is into the allowed country list, or false if not.
        """
        
        if cls.__IP2LocationIPTools.is_ipv4(ip):
            
            if str(cls.__databaseIpV4.get_country_short(ip)) in cls.__allowedCountries:
                return True
            else:
                return False
        
        elif cls.__IP2LocationIPTools.is_ipv6(ip):
            
            if str(cls.__databaseIpV6.get_country_short(ip)) in cls.__allowedCountries:
                return True
            else:
                return False
            
        else:
            traza.error("The IP[{}] is not ip4 or ip6 and can't be possessed, isIPInAllowedCountry returns True.".format(ip))
            return True
        
    def isInList(cls, ip : str, countryList: list):
        """
        This function return True if the country of IP is into the list, or false if not.
        """
        
        if cls.__IP2LocationIPTools.is_ipv4(ip):
            
            if str(cls.__databaseIpV4.get_country_short(ip)) in countryList:
                return True
            else:
                return False
        
        elif cls.__IP2LocationIPTools.is_ipv6(ip):
            
            if str(cls.__databaseIpV6.get_country_short(ip)) in countryList:
                return True
            else:
                return False
            
        else:
            traza.error("The IP[{}] is not ip4 or ip6 and can't be possessed, isInList returns False.".format(ip))
            return False
    
    def __downloadFile(cls, url, filePath):
        """
        This function is an auxiliary one useful to download database files.
        """

        try:
            f = urlopen(url)
            with open(filePath, "wb") as local_file:
                local_file.write(f.read())
                
        except Exception as e:
            raise Exception("Exception {} trying to download the file {} to the path {} ".format(e, url, filePath))
    