from datetime import datetime
from dateutil.parser import parse

def isDate(str):
    try:
        parse(str)
        return True
    except:
        return False

def IntDate(str):    
    d = parse(str)    
    return int(
        (datetime(
            d.year, 
            d.month, 
            d.day, 
            d.hour, 
            d.minute) 
        - datetime(1988, 1, 1)).total_seconds() / 60
    )
    
