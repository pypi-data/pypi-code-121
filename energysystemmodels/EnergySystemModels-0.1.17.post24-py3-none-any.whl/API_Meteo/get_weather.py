
import requests
import math

import os
import sys

cwd = os.getcwd()
print("+++--------------+++++++++=",cwd)
cwd=cwd.replace("\\", "/")
print("+++++------------++++++++++=",cwd)

#pip install requests[security]
 
sys.path.insert(0, os.path.join( os.path.dirname(__file__), "" , ""))
config_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
print("config path.........................",config_path)

from configparser import ConfigParser


def get_api_key():
    config = ConfigParser()
    config.read(config_path)
    print("................",config.read(config_path))
    return config['DonneesMeteo']['api']

def get_location():
    config = ConfigParser()
    config.read(config_path)
    #print(config['Location']['Town'])
    return config['Location']['Town'],config['Location']['lat'],config['Location']['lon']

 
def get_weather(api_key, location,lat,lon):
    if math.isnan(float(lat)) ^ math.isnan(float(lon)) :
        url="http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}".format(lat,lon, api_key)
       # print("url=",url)
    
    else:
        # url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(location, api_key)
         url="http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}".format(lat,lon, api_key)
        # print("url_town=",url)
       
    import time

    r = ''
    while r== '':
        try:
            #r = requests.get(url,timeout=(3.05, 27))
            r = requests.get(url,timeout=(5, 5))
          #  print("url reqtest=",url)
          #  print("r=",r)
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 9 seconds")
            time.sleep(9)
            print("Was a nice sleep, now let me continue...")
            continue

   
#    
  #  r = requests.get(url)
    print(r)
    return r.json()
 


#get_api_key()