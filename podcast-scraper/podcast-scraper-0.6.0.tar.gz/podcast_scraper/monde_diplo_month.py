import datetime

from selenium.webdriver import DesiredCapabilities
from testcontainers.selenium import BrowserWebDriverContainer

from podcast_scraper.api_scraper import ApiScraper


class MondeDiploMonth(ApiScraper):

    URL = "https://www.monde-diplomatique.fr/{year}/{month}/"

    def __init__(self, year, month):
        self.current_month = datetime.date(year, month, 1)

    def decrement(self):
        import dateutil.relativedelta

        last_month = self.current_month - dateutil.relativedelta.relativedelta(months=1)
        self.current_month = last_month

    def get_content(self, webdriver):
        webdriver.get(
            self.URL.format(
                year=str(self.current_month.year),
                month=str(self.current_month.month).zfill(
                    1 + len(str(self.current_month.month))
                ),
            )
        )
        first_selector = (
            "#contenu > div.contenu-principal > div.liste.alaune > ul > li > a"
        )
        second_selector = "#contenu > div.contenu-principal > div.liste.double > div.demi.gauche > ul > li > a"

        items = webdriver.find_elements_by_css_selector(
            first_selector + "," + second_selector
        )

        descs = []
        urls = []
        titles = []
        for item in items:
            url = item.get_attribute("href")
            urls.append(url)

            # either h3 or h4
            title = item.find_element_by_xpath(
                ".//div[contains(@class, 'titraille')]//*[self::h3 or self::h4]"
            ).text
            titles.append(title)

            # sometimes there is no desc at all
            try:
                desc = item.find_element_by_xpath(
                    ".//div[contains(@class, 'lintro')]"
                ).text
                descs.append(desc)
            except:
                descs.append(None)

        result = {"title": titles, "url": urls, "description": descs}
        self.decrement()
        return result

    def print_content(self, page_number=-1):
        with BrowserWebDriverContainer(DesiredCapabilities.CHROME) as chrome:
            webdriver = chrome.get_driver()
            while result := self.get_content(webdriver):
                print("Scrap page ", self.page_count)
                self.extracted_content.append(result)
                self.page_count += 1
                if page_number != -1 and page_number == self.page_count:
                    break

            return self
