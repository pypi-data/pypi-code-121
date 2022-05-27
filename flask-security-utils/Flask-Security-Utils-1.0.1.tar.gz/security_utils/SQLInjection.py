import logging
import base64
import re
from security_utils.DinamicBlockedIPList import DinamicBlockedIPList
from typing import TypeVar

rawStr = TypeVar('rawStr', bound=str)

traza = logging.getLogger(__name__)

class SQLInjection():
    
    """
    Clase de utilidad que permite realizar diferentes verificaciones de seguridad
    antes de ingresar los datos al sistema.
    """
    
    __instance = None
    __expressions = []
    __clsDinamicBlockedIPList = None
        
    def __new__(cls, dinamicBlockedIPList : DinamicBlockedIPList ):
        
        """
        Constructor of the SQLInjection class.
        """
        
        if (cls.__instance == None):
            
            #Regular expressions loaded by default
            cls.addExpression(r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(:))") #Detect SQL meta-characters
            cls.addExpression(r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))") #Regex for typical SQL Injection attack
            cls.addExpression(r"((\%27)|(\'))union") #Regex for Injection with the UNION keyword
            cls.addExpression(r"exec(\s|\+)+(s|x)p\w+") #Injection attacks on a MS SQL Server
            
            #Use the same singleton manager point
            cls.__clsDinamicBlockedIPList : DinamicBlockedIPList = dinamicBlockedIPList
                        
            #Create the class
            cls.__instance = object.__new__(cls)
        
        return cls.__instance
    
    @classmethod
    def clearExpressions(cls) -> None:
        
        """
        Method that removes all regular expressions from the class.
        """
        cls.__expressions.clear()
    
    @classmethod
    def addExpression(cls, expression : rawStr) -> None:
        
        """
        Method that allows adding regular expressions to be verified.
        """
        cls.__expressions.append(expression)
    
    
    @classmethod
    def detectSQLInjection(cls, dicForm : dict, ipToBlock : str) -> bool:
        
        """
        Method that allows to detect SQL injections in a post.
        """
        
        if cls.__clsDinamicBlockedIPList.isIPBlocked(ipToBlock) == True: return True
        
        for key, value in dicForm.items():
            
            if key in ['csrf_token','g-recaptcha-response']: continue
            if cls.detectSQLInjectionItem(value) == True: 
                cls.__clsDinamicBlockedIPList.blockIP(ipToBlock)
                traza.critical("An SQL Injection attempt was detected on {}, with the values {}.".format(key,str(value)))
                return True
        
        return False
    
    @classmethod
    def detectSQLInjectionVar(cls, var : str, ipToBlock : str) -> bool:
        
        """
        Method that allows to detect SQL injections in a variable.
        """
        
        if cls.__clsDinamicBlockedIPList.isIPBlocked(var) == True: return True
        
        if cls.detectSQLInjectionItem(var) == True: 
            cls.__clsDinamicBlockedIPList.blockIP(ipToBlock)
            traza.critical("SQL Injection attempt detected from IP[{}], with values {}.".format(ipToBlock,str(var)))
            return True
        
        return False
    
    @classmethod
    def detectSQLInjectionItem(cls, item : str) -> bool:
        
        """
        Method that allows detecting through regular expressions, hexadecimal attacks,
         SQL and base64 binary types.
        """
        
        def checkItem(strToCheck):
            
            auxStr = str(strToCheck)
            
            if auxStr == "None":
                return False
            
            for expression in cls.__expressions:
                if re.search(expression, auxStr) is not None:
                    return True
                
            return False
        
        try:
            
            decodedStr = base64.b64decode(item).decode('utf8')
            if checkItem(decodedStr) == True: return True
            if checkItem(item) == True: return True
            return False
            
        except:
            
            if checkItem(item) == True: return True
            return False
    