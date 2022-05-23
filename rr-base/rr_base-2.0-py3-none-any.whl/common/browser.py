"""
This module wrapping web utilities like initiate driver, basic actions, proxy server, and more
"""
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType


class SeleniumConfig:
    """Default parameters for initiate driver"""

    def __init__(self, chrome_driver_location=None, url='chrome://settings/cookies', headless=False, network=False,
                 page_load_timeout=20, implicitly_wait=10):
        self._url = url
        self._headless = headless
        self._network = network
        self._page_load_timeout = page_load_timeout
        self._implicitly_wait = implicitly_wait
        self._driver = self.__initiate_driver(chrome_driver_location=chrome_driver_location)

    def __initiate_driver(self, chrome_driver_location=None):
        """Creates a new instance of the chrome driver.
           Starts the service and then creates new instance of chrome driver.
        :Args
        - url - set end point
        - headless - gives the option to run the tests in the background
        - proxy - gives the option to record the traffic
        :Returns:
             - the driver object"""

        chrome_options = Options()
        capabilities = DesiredCapabilities.CHROME.copy()

        if self._headless:
            chrome_options.add_argument("--headless")

        if self._network:
            capabilities = webdriver.DesiredCapabilities.CHROME
            capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

        if chrome_driver_location is None:
            driver = webdriver.Chrome(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
                                      chrome_options=chrome_options,
                                      desired_capabilities=capabilities)
        else:
            driver = webdriver.Chrome(executable_path=chrome_driver_location,
                                      chrome_options=chrome_options,
                                      desired_capabilities=capabilities)

        driver.set_page_load_timeout(self._page_load_timeout)
        driver.get(self._url)
        driver.implicitly_wait(self._implicitly_wait)
        if not self._headless:
            driver.maximize_window()

        print(f"Started a new session: {driver.session_id}")
        return driver

    @property
    def get_driver(self):
        """return the log entry"""
        return self._driver

    @property
    def get_network_performance(self):
        """return the log entry"""
        return self._driver.get_log('performance')

    def get_url(self, url):
        """Loads a web page in the current browser session.
        :Args:
       - url - needs end point url for start session"""
        try:
            self._driver.get(url)
        except Exception as e:
            print(f'Failed to get url : {url}, reason : {e}')

    def get_data_from_url(self, url):
        """this function return the html body from specific url."""
        self.get_url(url)
        return self.__get_body()

    def __get_body(self):
        """this function return the html body."""
        try:
            return self._driver.find_element_by_tag_name("body").text
        except Exception as e:
            print(f"get body method exception:\n{e}")
            return

    def tear_down(self):
        """close the driver session."""
        self._driver.close()
        print("driver close")
