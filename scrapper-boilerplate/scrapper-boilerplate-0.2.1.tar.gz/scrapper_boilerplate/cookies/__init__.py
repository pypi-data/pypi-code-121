import pickle
from pathlib import Path


def cookies(driver):
    fileName = "cookies.pkl"
    fileName = Path(fileName)
    if fileName.is_file():
        print("Arquivo existe!")
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
    else:
        print("Arquivo não existe!")
        pickle.dump(driver.get_cookies() , open(f"{fileName}","wb"))

