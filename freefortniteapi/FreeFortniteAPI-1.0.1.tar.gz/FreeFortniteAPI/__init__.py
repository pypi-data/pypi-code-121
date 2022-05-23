import requests

class FortniteAPI:
    #aes
    def aes(type=None):
        if type == "build":
            try:
                return requests.get("https://fortnite-api.com/v2/aes").json()["data"]["build"]
            except:
                print("ERROR : can't connect to API please try again later.")

        elif type == "main key":
            try:
                return requests.get("https://fortnite-api.com/v2/aes").json()["data"]["mainKey"]
            except:
                print("ERROR : can't connect to API please try again later.")

        elif type == "updated":
            try:
                return requests.get("https://fortnite-api.com/v2/aes").json()["data"]["updated"]
            except:
                print("ERROR : can't connect to API please try again later.")


        elif type == None:
            print("no argument was given.")
        else:
            print(f'ERROR : the argument "{type}" is invalid.')

    #news
    def news(type=None):
        if type == "image gif":
            try:
                return requests.get("https://fortnite-api.com/v2/news/br").json()["data"]["image"]
            except:
                print("ERROR : can't connect to API please try again later.")

        elif type == "date":
            try:
                return requests.get("https://fortnite-api.com/v2/news/br").json()["data"]["date"]
            except:
                print("ERROR : can't connect to API please try again later.")
        
        elif type == "hash":
            try:
                return requests.get("https://fortnite-api.com/v2/news/br").json()["data"]["hash"]
            except:
                print("ERROR : can't connect to API please try again later.")


        elif type == None:
            print("no argument was given.")
        else:
            print(f'ERROR : the argument "{type}" is invalid.')