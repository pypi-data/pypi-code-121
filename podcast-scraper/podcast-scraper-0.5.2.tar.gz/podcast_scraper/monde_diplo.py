import re
import time

from selenium.webdriver.chrome.webdriver import WebDriver

from podcast_scraper.webdriver_scraper import WebdriverScraper


class MondeDiplo(WebdriverScraper):
    def connect(self, webdriver: WebDriver, user, password):
        connect = webdriver.find_element_by_css_selector("#session_connexion")
        connect.click()
        time.sleep(3)
        user_field = webdriver.find_element_by_css_selector(
            "#identification_sso > ul > li:nth-child(1) > input[type=email]"
        )
        user_field.send_keys(user)
        password_field = webdriver.find_element_by_css_selector(
            "#identification_sso > ul > li:nth-child(2) > input"
        )
        password_field.send_keys(password)
        validate = webdriver.find_element_by_css_selector(
            "#identification_sso > ul > li.submit > input[type=submit]"
        )
        validate.click()
        time.sleep(5)

    def get_urls(self, content):
        p = re.compile(
            r'<div class="track"><a href="(.+?\.mp3\?cle=[^"]+)"(?=[\s\S]+lien_pagination)',
            flags=re.MULTILINE,
        )
        m = p.findall(content)
        return {"url": m}

    def get_next(self, webdriver: WebDriver):
        try:
            next = webdriver.find_element_by_link_text("→")
            new_url = next.get_attribute("href")
            webdriver.get(new_url)
            return new_url
        except Exception as e:
            return False
