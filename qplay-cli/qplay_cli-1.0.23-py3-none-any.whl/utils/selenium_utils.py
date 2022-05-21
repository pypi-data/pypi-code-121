from retrying import retry
from selenium import webdriver

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

class Selenium():
    def __init__(self):
        self.x = False

    @staticmethod
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def get_browser(headless=True):
        opts = webdriver.ChromeOptions()

        if headless == True:
            opts.add_argument('headless')

        opts.add_argument('no-sandbox')
        browser = webdriver.Chrome(chrome_options=opts)

        return browser

    @staticmethod
    def get_element(browser, element_xpath, delay=10):
        if delay == None:
            return browser.find_element_by_xpath(element_xpath)
        try:
            element = WebDriverWait(browser, delay).until(
                EC.presence_of_element_located((By.XPATH, element_xpath)))
            return element
        except TimeoutException:
            print("Loading took too much time!")
            raise Exception("Timeout in first load")