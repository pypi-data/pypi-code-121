import json
from datetime import datetime, timedelta
import requests

class SchoolWare():
    def __init__(self, token:str) -> None:
        self.token = token
        if not self.__valid_token():
            raise ValueError("Token is invalid")  
        self._class = self.get_klas()

    def get_agenda(self, start:datetime, end:datetime) -> dict:
        """ Get the agenda from the schoolware """
        days = (end-start).days

        rooster = {}

        for day in range(days):
            res = requests.get(f'https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/AgendaPunt/?MinTot={start+timedelta(days=day)}&MaxVan={start+timedelta(days=day+1)}', cookies={'FPWebSession': self.token})
            if res.status_code != 200:
                raise ValueError("Could not get agenda")
            res_data = res.json()['data']

            datum = str(start+timedelta(days=day)).split(' ')[0]
            rooster[datum] = {}

            for agenda_item in res_data:
                if not self._class in agenda_item['Groep']:
                    continue

                class_name = agenda_item['VakNaam']
                title = agenda_item['Titel']
                room = agenda_item['LokaalCode']

                punt_gegevens = {
                    'Vak': class_name,
                    'Onderwerp': 'Geen onderwerp' if title == class_name else title,
                    'Lokaal': room if room else 'Geen lokaal',
                }

                van = ''.join(agenda_item['Van'].split(' ')[1])
                van_tijd = ':'.join(van.split(':')[:-1])

                tot = ''.join(agenda_item['Tot'].split(' ')[1])
                tot_tijd = ':'.join(tot.split(':')[:-1])

                rooster[datum][f'{van_tijd}-{tot_tijd}'] =  punt_gegevens
                
        return rooster

    def get_klas(self) -> str:
        res = self.__send_request(f'https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/PuntenbladGrid?BeoordelingMomentVan={datetime.now()-timedelta(weeks=9)}&BeoordelingMomentTot={datetime.now()}')
        res_data = res.json()
        
        try:
            _class =  res_data['data'][0]['KlasCode']
        except KeyError:
            raise ValueError("Unable to find class")
        return _class
    
    def __send_request(self, url:str) -> any:
        return requests.get(url, cookies={'FPWebSession': self.token})
    
    def __valid_token(self) -> bool:
        """ Checks if the token is valid """
        res = requests.get('https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/myschoolwareaccount', cookies={'FPWebSession': self.token})
        return res.status_code == 200



