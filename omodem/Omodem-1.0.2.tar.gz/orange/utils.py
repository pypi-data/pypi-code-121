from os import system, name
from time import sleep
from requests import post, get
from bs4 import BeautifulSoup


def clear():
    if name == 'nt':
        _ = system('cls')
  
    else:
        _ = system('clear')
  

def restart_local():
    post("http://192.168.0.1/goform/OrgNetworkRestart",data={"AskRgRestart":0})
    sleep(10)
    print("Nouvelle adresse ip publique : " + BeautifulSoup(get("http://192.168.0.1/overview.asp")
    .text, "html.parser").find('span', attrs={'class': 'severFontSize fontStyle01'}).get_text())