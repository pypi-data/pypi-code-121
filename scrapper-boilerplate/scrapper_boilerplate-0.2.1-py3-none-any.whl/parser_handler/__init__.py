import requests
from bs4 import BeautifulSoup
from requests.exceptions import InvalidSchema


def init_crawler(url):
    try:
        page = requests.get(url)

        if page.status_code != 200:
            print(f'[ERRO {page.status_code}] Site indisponivel, tente novamente mais tarde')
            return

        return BeautifulSoup(page.text, "lxml")

    except InvalidSchema:
        print('Algo deu errado!')
        return

    except ConnectionError:
        print('Não conseguiu se conectar na página!')
        return


def init_parser(html):
    return BeautifulSoup(html, "lxml")


def remove_whitespaces(text):
    return " ".join(text.split())


def remove_duplicates_on_list(array):
    return list(dict.fromkeys(array))
