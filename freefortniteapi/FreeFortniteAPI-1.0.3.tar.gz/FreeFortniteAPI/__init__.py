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


    #creator code
    def creator_code(code=None, type=None):
        if type == "code":
            try:
                return requests.get(f"https://fortnite-api.com/v2/creatorcode?name={code}").json()["data"]["code"]
            except:
                print("ERROR : can't connect to API please try again later.")

        elif type == "status":
            try:
                return requests.get(f"https://fortnite-api.com/v2/creatorcode?name={code}").json()["data"]["status"]
            except:
                print("ERROR : can't connect to API please try again later.")

                
        elif type == None:
            print("no argument was given.")
        else:
            print(f'ERROR : the argument "{type}" is invalid.')


    #creative mode
    def creative_mode_island(code=None, type=None):
        if type == "title":
            try:
                return requests.get(f"https://fortniteapi.io/v1/creative/island?code={code}",
                headers = {
                    "Authorization": "f3295740-a9367ef5-9bc9935a-40dbfcd2"}).json()["island"]["title"]
            except:
                print("ERROR : can't connect to API please try again later.")
        

        elif type == "description":
            try:
                return requests.get(f"https://fortniteapi.io/v1/creative/island?code={code}",
                headers = {
                    "Authorization": "f3295740-a9367ef5-9bc9935a-40dbfcd2"}).json()["island"]["description"]
            except:
                print("ERROR : can't connect to API please try again later.")


        elif type == "published date":
            try:
                return requests.get(f"https://fortniteapi.io/v1/creative/island?code={code}",
                headers = {
                    "Authorization": "f3295740-a9367ef5-9bc9935a-40dbfcd2"}).json()["island"]["publishedDate"]
            except:
                print("ERROR : can't connect to API please try again later.")

        
        elif type == "image":
            try:
                return requests.get(f"https://fortniteapi.io/v1/creative/island?code={code}",
                headers = {
                    "Authorization": "f3295740-a9367ef5-9bc9935a-40dbfcd2"}).json()["island"]["image"]
            except:
                print("ERROR : can't connect to API please try again later.")


        elif type == "creator":
            try:
                return requests.get(f"https://fortniteapi.io/v1/creative/island?code={code}",
                headers = {
                    "Authorization": "f3295740-a9367ef5-9bc9935a-40dbfcd2"}).json()["island"]["creator"]
            except:
                print("ERROR : can't connect to API please try again later.")



        elif type == None:
            print("no argument was given.")
        else:
            print(f'ERROR : the argument "{type}" is invalid.')