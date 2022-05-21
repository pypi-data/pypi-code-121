import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
from random import choice


class BrowserV2:
    user_agents: list = []
    __options = None

    @classmethod
    def get_agent(cls):
        if len(BrowserV2.user_agents) > 0:
            return choice(BrowserV2.user_agents)
        exit(1)

    @classmethod
    def delay(cls, start, end) -> None:
        Utils.time_to_sleep(start=start, end=end)

    def __init__(
            self,
            active_sleep: bool = False,
            profile_path: str = None,
            rotative_agent: bool = False,
            version_main: str = None
    ) -> None:

        self.__version_main = version_main
        self.__active_sleep = active_sleep
        self.__rotative_agent = rotative_agent
        BrowserV2.__options = uc.ChromeOptions()

        if profile_path is not None:
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)
            BrowserV2.__options.add_argument("--profile-directory=Default")
            BrowserV2.__options.add_argument('--user-data-dir=' + profile_path)

        BrowserV2.user_agents = list(Utils.get_agent_users())

        # just some options passing in to skip annoying popups
        BrowserV2.__options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        self.driver = uc.Chrome(options=BrowserV2.__options, version_main=self.__version_main)

    def navigate(self, url: str) -> None:
        if self.__active_sleep:
            Utils.time_to_sleep()
        if self.__rotative_agent:
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.get_agent()})
        self.driver.get(url)

    def close_driver(self) -> None:
        self.driver.close()

    def click(self, xpath: str):
        return self.driver.find_element(By.XPATH, xpath).click()

    def wait_to_click(self, xpath, time=10):
        return WebDriverWait(self.driver, time).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    def wait_frame_switch_to(self, xpath, time=10):
        WebDriverWait(self.driver, time).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath)))

    def switch_to_frame_default(self):
        self.driver.switch_to.default_content()

    def switch_to_frame(self, frame):
        self.driver.switch_to.frame(frame)

    def get_href(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).get_attribute('href')

    def get_src(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).get_attribute('src')

    def input(self, xpath, send):
        self.driver.find_element(By.XPATH, xpath).send_keys(send)

    def get_text(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).text

    def get_elements(self, xpath):
        return self.driver.find_elements(By.XPATH, xpath)

    def get_cookies(self):
        cookies = {}
        selenium_cookies = self.driver.get_cookies()
        for cookie in selenium_cookies:
            cookies[cookie['name']] = cookie['value']
        return cookies

    def element_is_present(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
            return True
        except:
            return False


class ChecksBypass(BrowserV2):
    def __init__(self, profile_path=None, rotative_agent=None, active_sleep=False):
        self.__profile_path = profile_path
        self.__active_sleep = active_sleep
        self.__rotative_agent = rotative_agent

        super().__init__(
            active_sleep=self.__active_sleep,
            profile_path=self.__profile_path,
            rotative_agent=self.__rotative_agent)

        self.__nowsecure_url = 'https://nowsecure.nl'
        self.__sannysoft = 'https://bot.sannysoft.com/'
        self.__httpbin_headers = 'http://httpbin.org/headers'
        self.__httpbin_ip = 'http://httpbin.org/ip'
        self.__amiunique = 'https://amiunique.org/fp'
        self.__ja3er = 'https://ja3er.com/'
        self.__antoinevastel = 'http://arh.antoinevastel.com/bots/areyouheadless'
        self.__creepjs = 'https://abrahamjuliot.github.io/creepjs/'
        self.__screen = 'https://abrahamjuliot.github.io/creepjs/tests/screen.html'
        self.__scrapfly = 'https://tools.scrapfly.io/api/fp/ja3?extended=1'

    def nowsecure(self):
        """
            Checks if your browser bypass the cloudfront protection
        """
        self.navigate(self.__nowsecure_url)

    def sannysoft(self):
        """
            Antibot check
        """
        self.navigate(self.__sannysoft)

    def httpbin_headers(self):
        """
            Checks request headers
        """
        self.navigate(self.__httpbin_headers)

    def httpbin_ip(self):
        """
            Checks ip address
        """
        self.navigate(self.__httpbin_ip)

    def amiunique(self):
        """
            My browser fingerprint
        """
        self.navigate(self.__amiunique)

    def ja3er(self):
        """
            Checks JA3 SSL Fingerprint
        """
        self.navigate(self.__ja3er)

    def antoinevastel(self):
        """
            Checks with you browser is headless
        """
        self.navigate(self.__antoinevastel)

    def creepjs(self):
        """
            The purpose of this project is to shed light on weaknesses and privacy leaks among modern anti-fingerprinting
            extensions and browsers.

            1. Detect and ignore API tampering (API lies)
            2. Fingerprint lie types
            3. Fingerprint extension code
            4. Fingerprint browser privacy settings
            5. Employ large-scale validation, but allow possible inconsistencies
            6. Feature detect and fingerprint new APIs that reveal high entropy
            7. Rely only on APIs that are the most difficult to spoof when generating a pure fingerprint
        """
        self.navigate(self.__creepjs)

    def screen(self):
        """
            Monitor fingerprint
        """
        self.navigate(self.__screen)

    def scrapfly(self):
        """
            Tools create by Scrapfly with propose of retuurn information about cipher suite (TLS)
        """
        self.navigate(self.__scrapfly)


class Utils:
    @staticmethod
    def time_to_sleep(start=2, end=10):
        from time import sleep
        from random import randint
        sleep(randint(start, end))

    @staticmethod
    def get_agent_users():
        agents = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 '
            'Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 '
            'Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 '
            'Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 '
            'Safari/537.36 '
        )
        return agents

