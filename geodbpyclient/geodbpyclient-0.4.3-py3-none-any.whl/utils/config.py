URL = "https://wft-geo-db.p.rapidapi.com"


def serverUrl():
    return URL


def headers(token):
    return {
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com",
        "X-RapidAPI-Key": token
    }
