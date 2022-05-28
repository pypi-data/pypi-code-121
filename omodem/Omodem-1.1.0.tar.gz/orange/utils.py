from os import system, name
from time import sleep
from requests import post, get
from bs4 import BeautifulSoup
from getpass import getpass

def clear():
    if name == 'nt':
        _ = system('cls')
  
    else:
        _ = system('clear')
  
def restart_local():
    post("http://192.168.0.1/goform/OrgNetworkRestart",data={"AskRgRestart":1})
    sleep(10)
    print("New public ip adress : " + BeautifulSoup(get("http://192.168.0.1/overview.asp")
    .text, "html.parser").find('span', attrs={'class': 'severFontSize fontStyle01'}).get_text())

def dashboard():
        login = get("http://192.168.0.1",timeout=3)
        stats = [
            str(i).split(">")[1].split("<")[0]
            for i in BeautifulSoup(login.text, "html.parser").find_all("span", {"class": "severFontSize fontStyle01"})
        ]
        print(f"\n🌐 Wifi : {stats[0]}\n🌍 Network access : {stats[1]}\n🔌 Wired network : {stats[2]}\n")

        if "Incorrect password !" in post("http://192.168.0.1/goform/OrgLogin", data={"OrgPassword" : getpass("Pass > ")}).text:
            print("❌ Incorrect password")
        else:
            clear()
            print("Public ip adress : " + BeautifulSoup(get("http://192.168.0.1/overview.asp")
            .text, "html.parser").find('span', attrs={'class': 'severFontSize fontStyle01'}).get_text())

            choice = int(input("Choose an option : \n1 - Change ip adress (restart local network)\n2 - exit\n> "))
            if choice == 1:
                restart_local()
            elif choice == 2:
                exit()