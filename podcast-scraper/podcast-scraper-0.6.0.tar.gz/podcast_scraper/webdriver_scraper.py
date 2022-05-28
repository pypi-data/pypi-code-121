import abc
import os

from selenium.webdriver import DesiredCapabilities
from testcontainers.selenium import BrowserWebDriverContainer
import pandas as pd


class WebdriverScraper:

    extracted_content = []

    @abc.abstractmethod
    def get_urls(self, content):
        ...

    @abc.abstractmethod
    def get_next(self, webdriver):
        ...

    def connect(self, webdriver, user, password):
        # dummy implementation, to be overrided
        pass

    def format_url(self):
        df = pd.concat([pd.DataFrame(url) for url in self.extracted_content])
        print(df.to_csv(index=None))

    def print_urls(self, url, page_number=-1):
        with BrowserWebDriverContainer(DesiredCapabilities.CHROME) as chrome:
            webdriver = chrome.get_driver()
            webdriver.get(url)
            self.connect(
                webdriver, os.getenv("USER", None), os.getenv("PASSWORD", None)
            )
            content = webdriver.page_source

            self.extracted_content.append(self.get_urls(content))
            page_count = 1
            print("Scrap page ", page_count)
            while bool(self.get_next(webdriver)) and (
                page_number == -1 or page_count < page_number
            ):
                result = webdriver.page_source
                self.extracted_content.append(self.get_urls(result))
                page_count += 1
                print("Scrap page ", page_count)

            self.format_url()
