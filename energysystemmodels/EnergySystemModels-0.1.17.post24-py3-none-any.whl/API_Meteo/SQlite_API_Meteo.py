import matplotlib.pyplot as plt
import json


import sys
sys.path.append("..") # Adds higher directory to python Modules_CTA path.

import sqlite3

from API_Meteo import get_weather
from get_weather import *

import datetime as dt


def API_meteo():
    T=0
# Save the current time to a variable ('t')
    
    t = dt.datetime.now()
    


    while True:
        delta = dt.datetime.now()-t
        
        if delta.seconds >= 10:
            #print("+5 secondes")
            # Update 't' variable to new time
            t = dt.datetime.now()
            #print(t)

##################################################################################
            conn = sqlite3.connect('BD_Meteo.db')
            c = conn.cursor()

# Create table
            c.execute('''CREATE TABLE if not exists Eaubonne
             (date text, Temperature real, Humidity real)''')
#####################################données météo##############################################################
# récupérer les données météo
            
            api_key = get_api_key()
#    print(api_key)
    
            location=get_location()
#    print(location[0])

            weather = get_weather(api_key, location[0],location[1],location[2])
# 
            #print(weather['main']['temp']-273.15,"°C",weather['main']['humidity'],"%")
            RH=weather['main']['humidity']
            T=weather['main']['temp']-273.15
            # print(weather)
            print("T = ",T," RH = ",RH)
            with open('data.json', 'w') as outfile:
                json.dump(weather, outfile)
################################################################################################    
# Insert a row of data
            dataForme_insert="INSERT INTO Eaubonne VALUES (?,?,?)"
            #import random
        
            #data_insert=(t,random.randint(-5, 35))
            data_insert=(t,weather['main']['temp']-273.15,weather['main']['humidity'])
            
            
            c.execute(dataForme_insert,data_insert)
            
            #plt.plot(t,weather['main']['temp']-273.15)
            #plt.show()
    

# Save (commit) the changes
            conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
            conn.close()
            
<<<<<<< HEAD
       # return T
=======
    #    return T
>>>>>>> c751d069316d9b805d3b17b04797fbd1bc04b23d
            
            
  

API_meteo()