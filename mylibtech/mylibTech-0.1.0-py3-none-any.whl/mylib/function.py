from dataclasses import dataclass
import os 
from datetime import datetime

def send_command(osname,command):
    """
    :this fuction is used to send command to operating system 

    """
    processedData={"command":command,"os specified":command,"time executed":""}
    os.system(command)
    return  processedData

# trying class
class validate_data:
    def try_hello(name,gender_input):
        gender=['male','female','other']
        if gender_input in gender:
            return f"hello {name} you have successfully registered"
        else:
            return f"hello {name} you have entered invalid data"
        


