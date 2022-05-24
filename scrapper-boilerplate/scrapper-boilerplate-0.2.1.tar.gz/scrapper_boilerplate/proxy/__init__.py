import os
from time import sleep
from random import choice
import requests
from selenium import webdriver
from dotenv import load_dotenv


def init_proxy():
    load_dotenv()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path=os.getenv('CHROMEDRIVER_PATH'))
    driver.get("https://www.sslproxies.org/")
    tbody = driver.find_element_by_tag_name("tbody")
    cell = tbody.find_elements_by_tag_name("tr")
    
    proxy_list = []
    for column in cell:
        column = column.text.split(" ")
        proxy = column[0]+":"+column[1]
        print(proxy)
        proxy_list.append(proxy)

    driver.quit()
    print("")

    os.system('clear')
    os.system('cls')

    # Proxy Connection

    print('Getting Proxies from graber...')
    sleep(2)
    os.system('clear')
    os.system('cls')
    target_proxy = choice(proxy_list)
    proxy = {"http": "http://"+ target_proxy}
    url = 'https://mobile.facebook.com/login'
    r = requests.get(url,  proxies=proxy)
    print("")
    print('Connecting using proxy' )
    print("")
    sts = r.status_code

    print(f'Proxy: {target_proxy} \nStatus: {sts}' )
    if sts == 200:
        return target_proxy
