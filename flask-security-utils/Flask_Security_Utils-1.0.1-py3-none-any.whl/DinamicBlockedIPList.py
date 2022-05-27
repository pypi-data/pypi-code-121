from datetime import datetime as dt
import logging
import csv

traza = logging.getLogger(__name__)

class DinamicBlockedIPList():
    
    """
    This class allows to manage all blocked IPs from one single point.
    """
    
    __IPBlocked = []
    __instance = None
    __ip_blocked_file = None
        
    def __new__(cls, ip_blocked_file = 'ip_blocked.csv'):
        
        """
        Constructor of the SQLInjection class.
        """
        
        if (cls.__instance == None):
            
            #Se csv file
            cls.__ip_blocked_file = ip_blocked_file
             
            # Load or or create the file with blocked ip 
            try:
                
                with open(cls.__ip_blocked_file) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    firstLine=True
                    for row in csv_reader:
                        if firstLine == True:
                            firstLine = False
                        else:
                            if len(row) > 1 : cls.__IPBlocked.append(row[0])
            except:
                
                header = ['IP_BLOCKED', 'DATE']

                with open(cls.__ip_blocked_file, 'w') as f:
                    cvs_writer = csv.writer(f)
                    cvs_writer.writerow(header)
                        
            #Create the class
            cls.__instance = object.__new__(cls)
        
        return cls.__instance
    

        
    @classmethod
    def blockIP(cls, ipToBlock : str) -> None:
        
        """
        Method that allows you to register an IP ban.
        """
        
        #Avoid duplicates
        if cls.isIPBlocked(ipToBlock) == True: return None
        
        #The IP is added to the list of blocks
        cls.__IPBlocked.append(ipToBlock)
        # The IP is saved for future attacks
        with open(cls.__ip_blocked_file, 'a+') as csv_file:
            ipBlockedWriter = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            ipBlockedWriter.writerow([ipToBlock, dt.now()])
    
    
    @classmethod
    def isIPBlocked(cls, ip: str) -> bool:
        
        if ip in cls.__IPBlocked: 
            return True
    