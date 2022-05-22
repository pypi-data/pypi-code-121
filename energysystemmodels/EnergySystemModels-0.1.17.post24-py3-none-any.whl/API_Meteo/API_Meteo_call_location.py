from API_Meteo import get_weather
#import get_weather
#pip install requests[security]

def API_call_location(lat:str,lon:str):

# )
    api_key = get_weather.get_api_key()
#    print(api_key)
    
    location=get_weather.get_location() #je passe à la ligne en dessous pour ajouter une lat et long comme paramètre
#    print(location[0])
    
    list_location=list(location)  #TypeError: 'tuple' object does not support item assignment
    list_location[1]=lat
    list_location[2]=lon
    
    location=tuple(list_location)
    #print("location",location)

    weather = get_weather.get_weather(api_key, location[0],location[1],location[2])
# 
    #print(weather['main']['temp']-273.15,"°C",weather['main']['humidity'],"%")
   # print(weather)
    T=weather['main']['temp']-273.15
    HR=weather['main']['humidity']
    return T,HR

#API_T_HR=API_call()
#print(API_T_HR[0])
 
# if __name__ == '__main__':
#     main()