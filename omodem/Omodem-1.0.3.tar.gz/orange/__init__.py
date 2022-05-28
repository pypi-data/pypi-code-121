from requests import RequestException, post, get
from getpass import getpass
from bs4 import BeautifulSoup
from orange.utils import *

def main():
    clear()
    try:
        login = get("http://192.168.0.1",timeout=3)
        stats = [
            str(i).split(">")[1].split("<")[0]
            for i in BeautifulSoup(login.text, "html.parser").find_all("span", {"class": "severFontSize fontStyle01"})
        ]
        print(f"\n🌐 Wifi : {stats[0]}\n🌍 Accès internet : {stats[1]}\n🔌 Réseau câblé : {stats[2]}\n")

        if "Incorrect password !" in post("http://192.168.0.1/goform/OrgLogin", data={"OrgPassword" : getpass("Mot de passe > ")}).text:
            print("❌ Le mot de passe est incorrect")
        else:
            clear()
            print("Adresse ip publique : " + BeautifulSoup(get("http://192.168.0.1/overview.asp")
            .text, "html.parser").find('span', attrs={'class': 'severFontSize fontStyle01'}).get_text())

            choice = int(input("Que faire ? : \n1 - Changer d'ip (redémarre le réseau local\n2 - quitter\n> "))
            if choice == 1:
                restart_local
            elif choice == 2:
                exit()
    except RequestException:
        print(
            "La box me répond un code d'erreur ou je ne parviens tout simpletement pas à l'atteindre"
        )

if __name__ == '__main__':
    main()