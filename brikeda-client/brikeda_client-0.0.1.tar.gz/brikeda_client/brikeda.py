import requests
import urllib3
urllib3.disable_warnings()


class Brikeda:
    def __init__(self,url,key,robot=""):
        self.url=url
        self.key=key
        self.robot =robot
        print(f'Robot {self.robot} is initialized')

    def WeatherForecast(self):
        furl=self.url + "/api/AI/Weather"
       # print(furl)
        response = requests.get(furl, verify=False)
        print(response.content)
    def SyncMessages(self,message):
        newurl=self.url + '/api/AI/message'
        print(newurl)     
        response = requests.post(newurl, json ={"key": self.key,  "message": message}, verify=False)
        print(response.content)
    def TestIt(self,message):
        print(f"you said: {message}" )