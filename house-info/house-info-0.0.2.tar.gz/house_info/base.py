from typing import List
from bs4 import BeautifulSoup, ResultSet
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver


class BaseSelRequest:
    """
    selenium을 사용하는 요청 Base
    """

    URL: str = "url"

    def __init__(self, chrome_driver_path: str, page: int = 1) -> None:
        self.__service = Service(chrome_driver_path)
        self.page = page

    def browser_open_headless(self) -> WebDriver:
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        browser = Chrome(service=self.__service, options=chrome_option)
        browser.implicitly_wait(2)
        browser.get(self.URL)
        return browser

    def get_page_source(self, browser: WebDriver):
        page_source = browser.page_source
        return page_source

    def parse_html(self, page_source) -> ResultSet:
        soup = BeautifulSoup(page_source, "html.parser")
        return soup

    def get_post_list(self, soup):
        pass

    def move_next_page(self, browser, page):
        browser.execute_script(f"javascript({page})")
        return browser

    def create_post_list_sources(self) -> List[ResultSet]:
        pass
